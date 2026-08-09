import os
import sys
import datetime
import time
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.cloud import bigquery

GCP_PROJECT = os.environ.get("GOOGLE_PROJECT_ID", "project-743aab84-f9a5-4ec7-954")
BQ_DATASET = "national_audits"
BQ_TABLE = "google_photos_index"
FULL_TABLE_ID = f"{GCP_PROJECT}.{BQ_DATASET}.{BQ_TABLE}"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRET_FILE = os.path.join(SCRIPT_DIR, "client_secret.json")
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token_photos.json")
RESUME_TOKEN_FILE = os.path.join(SCRIPT_DIR, "photos_resume_token.txt")

SCOPES = ["https://www.googleapis.com/auth/photoslibrary.readonly"]

def get_photos_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("[AUTH] Launching browser to authenticate Google Photos access...")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token_file:
            token_file.write(creds.to_json())
    return build("photoslibrary", "v1", credentials=creds, static_discovery=False)

BQ_SCHEMA = [
    bigquery.SchemaField("photo_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("filename", "STRING"),
    bigquery.SchemaField("mime_type", "STRING"),
    bigquery.SchemaField("creation_time", "TIMESTAMP"),
    bigquery.SchemaField("camera_make", "STRING"),
    bigquery.SchemaField("camera_model", "STRING"),
    bigquery.SchemaField("focal_length", "FLOAT"),
    bigquery.SchemaField("aperture", "FLOAT"),
    bigquery.SchemaField("iso_equivalent", "INTEGER"),
    bigquery.SchemaField("ingest_timestamp", "TIMESTAMP"),
]

def ensure_table(bq_client):
    try:
        bq_client.get_table(FULL_TABLE_ID)
    except Exception:
        table_ref = bigquery.Table(FULL_TABLE_ID, schema=BQ_SCHEMA)
        table_ref.description = "Google Photos Metadata Index"
        bq_client.create_table(table_ref)

def scan_google_photos():
    print("=" * 60)
    print("  OSINTNeoAi GOOGLE PHOTOS SCANNER  ")
    print("=" * 60)
    
    service = get_photos_service()
    bq_client = bigquery.Client(project=GCP_PROJECT)
    ensure_table(bq_client)

    page_token = None
    if os.path.exists(RESUME_TOKEN_FILE):
        with open(RESUME_TOKEN_FILE, "r") as f:
            page_token = f.read().strip()
            if not page_token: page_token = None
            else: print(f"[PHOTOS] Resuming from token: {page_token[:10]}...")

    batch_size = 2000
    current_batch = []
    total_processed = 0
    scan_ts = datetime.datetime.utcnow().isoformat() + "Z"
    last_save_time = time.time()

    print("[PHOTOS] Scanning Google Photos library...")
    
    while True:
        try:
            results = service.mediaItems().list(pageSize=100, pageToken=page_token).execute()
        except Exception as e:
            print(f"[!] Error fetching photos: {e}")
            break

        items = results.get('mediaItems', [])
        if not items:
            break

        for item in items:
            meta = item.get('mediaMetadata', {})
            photo_meta = meta.get('photo', {})
            
            row = {
                "photo_id": item.get('id'),
                "filename": item.get('filename'),
                "mime_type": item.get('mimeType'),
                "creation_time": meta.get('creationTime'),
                "camera_make": photo_meta.get('cameraMake'),
                "camera_model": photo_meta.get('cameraModel'),
                "focal_length": photo_meta.get('focalLength'),
                "aperture": photo_meta.get('apertureFNumber'),
                "iso_equivalent": photo_meta.get('isoEquivalent'),
                "ingest_timestamp": scan_ts
            }
            current_batch.append(row)
            
        page_token = results.get('nextPageToken')

        # Check if 10 minutes have passed OR we hit batch size OR no more pages
        if len(current_batch) >= batch_size or not page_token or (time.time() - last_save_time > 600):
            if current_batch:
                job_config = bigquery.LoadJobConfig(schema=BQ_SCHEMA, write_disposition=bigquery.WriteDisposition.WRITE_APPEND, source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON)
                bq_client.load_table_from_json(current_batch, FULL_TABLE_ID, job_config=job_config).result()
                
                total_processed += len(current_batch)
                print(f"  ... Ingested batch. Total processed: {total_processed}")
            
            if page_token:
                with open(RESUME_TOKEN_FILE, "w") as f:
                    f.write(page_token)
            else:
                if os.path.exists(RESUME_TOKEN_FILE):
                    os.remove(RESUME_TOKEN_FILE)
            
            current_batch = []
            
            # Pause if triggered by 10-minute rule
            if time.time() - last_save_time > 600:
                print("[AUTOSAVE] 10-minute interval reached. Data saved. Pausing for 10 seconds...")
                time.sleep(10)
                last_save_time = time.time()

        if not page_token:
            break

    print(f"[+] Google Photos Scan Complete! {total_processed} items indexed.")

if __name__ == "__main__":
    scan_google_photos()
