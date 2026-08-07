import os
import io
import datetime
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.cloud import bigquery

GCP_PROJECT = os.environ.get("GOOGLE_PROJECT_ID", "project-743aab84-f9a5-4ec7-954")
BQ_DATASET = "national_audits"
BQ_TABLE = "drive_photos_exif"
FULL_TABLE_ID = f"{GCP_PROJECT}.{BQ_DATASET}.{BQ_TABLE}"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token.json")

def get_drive_service():
    if not os.path.exists(TOKEN_FILE):
        raise Exception("token.json not found! Authenticate Drive first.")
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, ["https://www.googleapis.com/auth/drive.readonly"])
    return build("drive", "v3", credentials=creds)

def get_decimal_from_dms(dms, ref):
    try:
        degrees = dms[0]
        minutes = dms[1] / 60.0
        seconds = dms[2] / 3600.0
        if ref in ['S', 'W']:
            degrees = -degrees
            minutes = -minutes
            seconds = -seconds
        return round(degrees + minutes + seconds, 5)
    except Exception:
        return None

def extract_exif(image_bytes):
    exif_data = {
        "datetime": None,
        "camera_make": None,
        "camera_model": None,
        "latitude": None,
        "longitude": None
    }
    
    try:
        image = Image.open(io.BytesIO(image_bytes))
        if not hasattr(image, '_getexif'):
            return exif_data
            
        exif_info = image._getexif()
        if not exif_info:
            return exif_data

        for tag, value in exif_info.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "DateTimeOriginal" or decoded == "DateTime":
                exif_data["datetime"] = str(value)
            elif decoded == "Make":
                exif_data["camera_make"] = str(value)
            elif decoded == "Model":
                exif_data["camera_model"] = str(value)
            elif decoded == "GPSInfo":
                gps_data = {}
                for t in value:
                    sub_decoded = GPSTAGS.get(t, t)
                    gps_data[sub_decoded] = value[t]
                
                lat = gps_data.get('GPSLatitude')
                lat_ref = gps_data.get('GPSLatitudeRef')
                lon = gps_data.get('GPSLongitude')
                lon_ref = gps_data.get('GPSLongitudeRef')
                
                if lat and lat_ref and lon and lon_ref:
                    exif_data["latitude"] = get_decimal_from_dms(lat, lat_ref)
                    exif_data["longitude"] = get_decimal_from_dms(lon, lon_ref)

    except Exception as e:
        pass
        
    return exif_data

BQ_SCHEMA = [
    bigquery.SchemaField("file_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("file_name", "STRING"),
    bigquery.SchemaField("mime_type", "STRING"),
    bigquery.SchemaField("datetime_original", "STRING"),
    bigquery.SchemaField("camera_make", "STRING"),
    bigquery.SchemaField("camera_model", "STRING"),
    bigquery.SchemaField("latitude", "FLOAT"),
    bigquery.SchemaField("longitude", "FLOAT"),
    bigquery.SchemaField("ingest_timestamp", "TIMESTAMP"),
]

def ensure_table(bq_client):
    table_ref = bigquery.Table(FULL_TABLE_ID, schema=BQ_SCHEMA)
    try:
        bq_client.get_table(FULL_TABLE_ID)
    except Exception:
        bq_client.create_table(table_ref)

def ingest_photos():
    print("[PHOTOS] Connecting to Drive and BigQuery...")
    service = get_drive_service()
    bq_client = bigquery.Client(project=GCP_PROJECT)
    ensure_table(bq_client)
    
    # Query BigQuery to find all images
    query = f"""
    SELECT file_id, file_name, mime_type
    FROM `{GCP_PROJECT}.national_audits.drive_file_index`
    WHERE mime_type LIKE 'image/%'
    """
    
    print("[PHOTOS] Fetching list of images from Drive Index...")
    results = list(bq_client.query(query).result())
    print(f"[PHOTOS] Found {len(results)} images in Drive index.")
    
    if not results:
        print("[!] No images to process.")
        return

    rows_to_insert = []
    scan_ts = datetime.datetime.utcnow().isoformat() + "Z"
    
    processed = 0
    with_gps = 0

    print("[PHOTOS] Beginning EXIF Extraction...")
    for f in results:
        file_id = f.file_id
        file_name = f.file_name
        
        try:
            request = service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                
            image_bytes = fh.getvalue()
            exif = extract_exif(image_bytes)
            
            row = {
                "file_id": file_id,
                "file_name": file_name,
                "mime_type": f.mime_type,
                "datetime_original": exif["datetime"],
                "camera_make": exif["camera_make"],
                "camera_model": exif["camera_model"],
                "latitude": exif["latitude"],
                "longitude": exif["longitude"],
                "ingest_timestamp": scan_ts
            }
            rows_to_insert.append(row)
            processed += 1
            
            if exif["latitude"] is not None:
                with_gps += 1
                print(f"  [+] Found GPS coordinates in: {file_name}")
                
            if len(rows_to_insert) >= 100:
                job_config = bigquery.LoadJobConfig(schema=BQ_SCHEMA, write_disposition=bigquery.WriteDisposition.WRITE_APPEND, source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON)
                bq_client.load_table_from_json(rows_to_insert, FULL_TABLE_ID, job_config=job_config).result()
                rows_to_insert = []
                print(f"  ... Ingested batch. Total processed: {processed}")
                
        except Exception as e:
            print(f"  [!] Error processing {file_name}: {e}")

    # Final batch
    if rows_to_insert:
        job_config = bigquery.LoadJobConfig(schema=BQ_SCHEMA, write_disposition=bigquery.WriteDisposition.WRITE_APPEND, source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON)
        bq_client.load_table_from_json(rows_to_insert, FULL_TABLE_ID, job_config=job_config).result()

    print(f"\n[✓] Photos Ingestion Complete!")
    print(f"    Total processed: {processed}")
    print(f"    Images with GPS data: {with_gps}")

if __name__ == "__main__":
    ingest_photos()
