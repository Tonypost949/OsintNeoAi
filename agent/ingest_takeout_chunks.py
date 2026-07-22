import os
import sys
import json
import glob
import shutil
import subprocess
import zipfile
import datetime
import io
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from google.cloud import bigquery

sys.stdout.reconfigure(encoding="utf-8")

GCP_PROJECT = "project-743aab84-f9a5-4ec7-954"
DATASET_ID = "national_audits"
TABLE_ID = "google_photos_index"
FULL_TABLE_ID = f"{GCP_PROJECT}.{DATASET_ID}.{TABLE_ID}"
REMOTE_DIR = "gdrive:Sharedall/takeouts all 22226"

LOCAL_CHUNK_DIR = r"G:\takeout_chunks"
PROGRESS_FILE = r"C:\OsintNeoAi\chunk_progress_tracker.json"
CHUNK_SIZE = 5  # Process 5 ZIP files per chunk

def ensure_bq_table(client):
    schema = [
        bigquery.SchemaField("photo_id", "STRING"),
        bigquery.SchemaField("filename", "STRING"),
        bigquery.SchemaField("mime_type", "STRING"),
        bigquery.SchemaField("creation_time", "TIMESTAMP"),
        bigquery.SchemaField("camera_make", "STRING"),
        bigquery.SchemaField("camera_model", "STRING"),
        bigquery.SchemaField("focal_length", "FLOAT"),
        bigquery.SchemaField("aperture", "FLOAT"),
        bigquery.SchemaField("iso_equivalent", "INTEGER"),
        bigquery.SchemaField("latitude", "FLOAT"),
        bigquery.SchemaField("longitude", "FLOAT"),
        bigquery.SchemaField("description", "STRING"),
        bigquery.SchemaField("source_zip", "STRING"),
        bigquery.SchemaField("file_path", "STRING"),
        bigquery.SchemaField("ingest_timestamp", "TIMESTAMP"),
    ]
    try:
        table = client.get_table(FULL_TABLE_ID)
        existing = {f.name for f in table.schema}
        new_schema = list(table.schema)
        added = False
        for f in schema:
            if f.name not in existing:
                new_schema.append(f)
                added = True
        if added:
            table.schema = new_schema
            client.update_table(table, ["schema"])
            print(f"[BQ] Schema updated for {FULL_TABLE_ID}")
    except Exception:
        print(f"[BQ] Creating table {FULL_TABLE_ID}...")
        t = bigquery.Table(FULL_TABLE_ID, schema=schema)
        client.create_table(t)

def get_decimal_from_dms(dms, ref):
    try:
        deg = float(dms[0])
        mn = float(dms[1]) / 60.0
        sec = float(dms[2]) / 3600.0
        val = deg + mn + sec
        if ref in ['S', 'W']:
            val = -val
        return round(val, 6)
    except Exception:
        return None

def extract_exif_data(img_path):
    info = {"datetime": None, "make": None, "model": None, "lat": None, "lon": None}
    try:
        with Image.open(img_path) as img:
            exif = img._getexif()
            if not exif:
                return info
            for tag, val in exif.items():
                decoded = TAGS.get(tag, tag)
                if decoded in ["DateTimeOriginal", "DateTime"]:
                    info["datetime"] = str(val)
                elif decoded == "Make":
                    info["make"] = str(val).strip()
                elif decoded == "Model":
                    info["model"] = str(val).strip()
                elif decoded == "GPSInfo":
                    gps = {}
                    for t in val:
                        sub = GPSTAGS.get(t, t)
                        gps[sub] = val[t]
                    lat = gps.get("GPSLatitude")
                    lat_ref = gps.get("GPSLatitudeRef")
                    lon = gps.get("GPSLongitude")
                    lon_ref = gps.get("GPSLongitudeRef")
                    if lat and lat_ref and lon and lon_ref:
                        info["lat"] = get_decimal_from_dms(lat, lat_ref)
                        info["lon"] = get_decimal_from_dms(lon, lon_ref)
    except Exception:
        pass
    return info

def parse_json_metadata(json_path):
    try:
        with open(json_path, 'r', encoding='utf-8', errors='ignore') as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return None
        
        title = data.get("title") or os.path.basename(json_path).replace(".json", "")
        desc = data.get("description", "")
        
        creation_time_str = None
        taken_time = data.get("photoTakenTime", {})
        if isinstance(taken_time, dict):
            ts = taken_time.get("timestamp")
            if ts:
                try:
                    dt = datetime.datetime.fromtimestamp(float(ts), datetime.timezone.utc)
                    creation_time_str = dt.isoformat().replace("+00:00", "Z")
                except Exception:
                    pass
            if not creation_time_str and taken_time.get("formatted"):
                creation_time_str = taken_time.get("formatted")

        lat = None
        lon = None
        geo = data.get("geoData", {})
        if isinstance(geo, dict):
            lat = geo.get("latitude")
            lon = geo.get("longitude")
            if lat == 0.0 and lon == 0.0:
                geo_exif = data.get("geoDataExif", {})
                if isinstance(geo_exif, dict):
                    lat = geo_exif.get("latitude") or None
                    lon = geo_exif.get("longitude") or None
            if lat == 0.0 and lon == 0.0:
                lat = None
                lon = None

        return {
            "filename": title,
            "creation_time": creation_time_str,
            "latitude": float(lat) if lat is not None else None,
            "longitude": float(lon) if lon is not None else None,
            "description": desc[:1000] if desc else None
        }
    except Exception:
        return None

def process_extracted_folder(folder_path, chunk_tag, bq_client):
    print(f"\n[CHUNK] Scanning extracted directory: {folder_path}")
    rows = []
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    
    # 1. Look for .json metadata files
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), folder_path)
            
            if file.endswith('.json') and not file.startswith('metadata'):
                json_full = os.path.join(root, file)
                meta = parse_json_metadata(json_full)
                if meta:
                    # Look for corresponding image file
                    img_file = file.replace('.json', '')
                    img_path = os.path.join(root, img_file)
                    exif = extract_exif_data(img_path) if os.path.exists(img_path) else {}

                    row = {
                        "photo_id": f"{chunk_tag}:{rel_path}",
                        "filename": meta["filename"],
                        "mime_type": "image/jpeg" if meta["filename"].lower().endswith(('.jpg', '.jpeg')) else "image/png",
                        "creation_time": meta["creation_time"] or exif.get("datetime"),
                        "camera_make": exif.get("make"),
                        "camera_model": exif.get("model"),
                        "focal_length": None,
                        "aperture": None,
                        "iso_equivalent": None,
                        "latitude": meta["latitude"] or exif.get("lat"),
                        "longitude": meta["longitude"] or exif.get("lon"),
                        "description": meta["description"],
                        "source_zip": chunk_tag,
                        "file_path": rel_path,
                        "ingest_timestamp": now_iso
                    }
                    rows.append(row)
            elif file.lower().endswith(('.jpg', '.jpeg', '.png', '.heic', '.webp')) and not os.path.exists(os.path.join(root, file + '.json')):
                # Standalone image without JSON metadata
                img_full = os.path.join(root, file)
                exif = extract_exif_data(img_full)
                row = {
                    "photo_id": f"{chunk_tag}:{rel_path}",
                    "filename": file,
                    "mime_type": "image/jpeg" if file.lower().endswith(('.jpg', '.jpeg')) else "image/png",
                    "creation_time": exif.get("datetime"),
                    "camera_make": exif.get("make"),
                    "camera_model": exif.get("model"),
                    "focal_length": None,
                    "aperture": None,
                    "iso_equivalent": None,
                    "latitude": exif.get("lat"),
                    "longitude": exif.get("lon"),
                    "description": None,
                    "source_zip": chunk_tag,
                    "file_path": rel_path,
                    "ingest_timestamp": now_iso
                }
                rows.append(row)

            if len(rows) >= 500:
                flush_rows_to_bq(rows, bq_client)
                rows = []

    if rows:
        flush_rows_to_bq(rows, bq_client)
        rows = []

def flush_rows_to_bq(rows, bq_client):
    if not rows:
        return
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
    )
    job = bq_client.load_table_from_json(rows, FULL_TABLE_ID, job_config=job_config)
    job.result()
    print(f"  [BQ] Loaded chunk batch of {len(rows)} records into {FULL_TABLE_ID}.")

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {"completed_chunks": [], "completed_zips": []}

def save_progress(progress):
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

def main():
    bq_client = bigquery.Client(project=GCP_PROJECT)
    ensure_bq_table(bq_client)
    progress = load_progress()

    os.makedirs(LOCAL_CHUNK_DIR, exist_ok=True)

    # STEP 1: Process Local Takeout & DCIM Folders first (Local Chunk 0)
    local_dirs = [
        (r"G:\_folders\takeout-20260321T071554Z-001\Takeout", "LOCAL_TAKEOUT_20260321"),
        (r"G:\_folders\DCIM", "LOCAL_DCIM"),
        (r"G:\_folders\Pictures", "LOCAL_PICTURES"),
        (r"G:\_folders\Camera Roll", "LOCAL_CAMERA_ROLL")
    ]
    
    for ldir, tag in local_dirs:
        if tag not in progress["completed_chunks"] and os.path.exists(ldir):
            print(f"\n==========================================")
            print(f" PROCESSING LOCAL CHUNK: {tag}")
            print(f"==========================================")
            process_extracted_folder(ldir, tag, bq_client)
            progress["completed_chunks"].append(tag)
            save_progress(progress)

    # STEP 2: Process Remote Google Drive Takeout ZIPs in Chunks
    zip_cache_file = r"C:\OsintNeoAi\takeout_zip_list_cache.json"
    all_zips = []
    if os.path.exists(zip_cache_file):
        try:
            with open(zip_cache_file, 'r') as f:
                all_zips = json.load(f)
            print(f"[CACHE] Loaded {len(all_zips)} ZIP names from local cache.")
        except Exception:
            pass

    if not all_zips:
        print(f"\n[REMOTE] Querying remote ZIP list from Google Drive ({REMOTE_DIR})...")
        cmd = ["rclone", "lsf", REMOTE_DIR, "--include", "*.zip"]
        for attempt in range(1, 5):
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                all_zips = [f.strip() for f in res.stdout.splitlines() if f.strip().endswith(".zip")]
                with open(zip_cache_file, 'w') as f:
                    json.dump(all_zips, f, indent=2)
                break
            print(f" [!] rclone lsf attempt {attempt} failed, retrying in 3s...")
            import time
            time.sleep(3)
    
    remaining_zips = [z for z in all_zips if z not in progress["completed_zips"]]
    print(f"[REMOTE] Total ZIPs: {len(all_zips)} | Remaining: {len(remaining_zips)}")

    # Chunk the remaining zips into batches of CHUNK_SIZE
    chunk_batches = [remaining_zips[i:i+CHUNK_SIZE] for i in range(0, len(remaining_zips), CHUNK_SIZE)]

    for chunk_idx, batch in enumerate(chunk_batches):
        chunk_name = f"chunk_{chunk_idx+1}_{len(chunk_batches)}"
        chunk_path = os.path.join(LOCAL_CHUNK_DIR, chunk_name)
        os.makedirs(chunk_path, exist_ok=True)
        
        print(f"\n==========================================")
        print(f" PROCESSING REMOTE BATCH CHUNK {chunk_idx+1}/{len(chunk_batches)} ({len(batch)} ZIPs)")
        print(f" ZIPs: {', '.join(batch)}")
        print(f"==========================================")

        for zip_name in batch:
            remote_zip_path = f"{REMOTE_DIR}/{zip_name}"
            local_zip_dest = os.path.join(chunk_path, zip_name)
            
            print(f" [RCLONE] Downloading {zip_name} -> {local_zip_dest}...")
            dl_cmd = ["rclone", "copyto", remote_zip_path, local_zip_dest, "--drive-chunk-size", "64M", "--retries", "5", "--low-level-retries", "10"]
            
            dl_success = False
            try:
                dl_res = subprocess.run(dl_cmd, capture_output=True, text=True)
                if dl_res.returncode == 0 and os.path.exists(local_zip_dest):
                    dl_success = True
                else:
                    print(f"  [!] rclone download returned code {dl_res.returncode}: {dl_res.stderr[:200]}")
            except Exception as e:
                print(f"  [!] Exception during download of {zip_name}: {e}")

            if dl_success:
                extract_target = os.path.join(chunk_path, zip_name.replace(".zip", ""))
                print(f" [EXTRACT] Selectively extracting photos/json from {zip_name}...")
                try:
                    with zipfile.ZipFile(local_zip_dest, 'r') as z:
                        target_members = [
                            m for m in z.namelist()
                            if m.lower().endswith(('.json', '.jpg', '.jpeg', '.png', '.heic', '.webp'))
                        ]
                        z.extractall(extract_target, members=target_members)
                    os.remove(local_zip_dest)  # remove downloaded zip immediately to save space
                    
                    print(f" [INGEST] Ingesting photos from {zip_name}...")
                    process_extracted_folder(extract_target, zip_name, bq_client)
                    
                    shutil.rmtree(extract_target, ignore_errors=True)  # remove extracted folder
                    progress["completed_zips"].append(zip_name)
                    save_progress(progress)
                except Exception as e:
                    print(f" [!] Error extracting {zip_name}: {e}")
            else:
                print(f" [!] Skipping {zip_name} due to download error. Marking as attempted.")
                if "failed_zips" not in progress:
                    progress["failed_zips"] = []
                progress["failed_zips"].append(zip_name)
                save_progress(progress)

        # Clean up chunk directory
        shutil.rmtree(chunk_path, ignore_errors=True)
        print(f"[CHUNK COMPLETED] Batch {chunk_idx+1}/{len(chunk_batches)} done & cleaned up.")

    print("\n[✓] ALL TAKEOUT CHUNKS SUCCESSFULLY PROCESSED AND LOADED TO BIGQUERY!")

if __name__ == "__main__":
    main()
