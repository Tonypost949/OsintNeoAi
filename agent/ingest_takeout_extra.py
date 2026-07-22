import os
import sys
import json
import re
import datetime
import subprocess
import zipfile
from google.cloud import bigquery

sys.stdout.reconfigure(encoding="utf-8")

GCP_PROJECT = os.environ.get("GOOGLE_PROJECT_ID", "project-743aab84-f9a5-4ec7-954")
BQ_DATASET = "national_audits"
TEMP_DIR = "G:\\temp_takeout"

def ensure_tables(bq_client):
    # 1. Location History
    loc_schema = [
        bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("latitude", "FLOAT64"),
        bigquery.SchemaField("longitude", "FLOAT64"),
        bigquery.SchemaField("accuracy", "INT64"),
        bigquery.SchemaField("velocity", "INT64"),
        bigquery.SchemaField("altitude", "INT64")
    ]
    loc_table_id = f"{GCP_PROJECT}.{BQ_DATASET}.takeout_location_history"
    try:
        bq_client.get_table(loc_table_id)
        print(f"[BQ] Table {loc_table_id} already exists.")
    except Exception:
        table = bigquery.Table(loc_table_id, schema=loc_schema)
        bq_client.create_table(table)
        print(f"[BQ] Created table {loc_table_id}.")

    # 2. Bookmarks
    bm_schema = [
        bigquery.SchemaField("added_timestamp", "TIMESTAMP"),
        bigquery.SchemaField("title", "STRING"),
        bigquery.SchemaField("url", "STRING"),
        bigquery.SchemaField("folder_path", "STRING")
    ]
    bm_table_id = f"{GCP_PROJECT}.{BQ_DATASET}.takeout_chrome_bookmarks"
    try:
        bq_client.get_table(bm_table_id)
        print(f"[BQ] Table {bm_table_id} already exists.")
    except Exception:
        table = bigquery.Table(bm_table_id, schema=bm_schema)
        bq_client.create_table(table)
        print(f"[BQ] Created table {bm_table_id}.")

def download_zip(zip_name):
    os.makedirs(TEMP_DIR, exist_ok=True)
    local_path = os.path.join(TEMP_DIR, zip_name)
    if os.path.exists(local_path):
        print(f"[DOWNLOAD] {zip_name} already exists locally.")
        return local_path
    
    remote_path = f"gdrive:Sharedall/takeouts all 22226/{zip_name}"
    print(f"[DOWNLOAD] Copying {zip_name} from Google Drive to G: drive...")
    cmd = ["rclone", "copyto", remote_path, local_path]
    subprocess.run(cmd, check=True)
    print(f"[DOWNLOAD] Completed download of {zip_name}.")
    return local_path

def parse_and_load_bookmarks(bq_client, local_zip_path, inner_path):
    print(f"[BOOKMARKS] Parsing bookmarks from local ZIP...")
    rows = []
    with zipfile.ZipFile(local_zip_path) as z:
        with z.open(inner_path) as f:
            html_content = f.read().decode("utf-8", errors="ignore")
            matches = re.findall(r'<A HREF="([^"]+)"[^>]*ADD_DATE="([^"]*)"[^>]*>([^<]+)</A>', html_content)
            for url, add_date, title in matches:
                try:
                    ts = None
                    if add_date:
                        ts = datetime.datetime.utcfromtimestamp(int(add_date)).isoformat() + "Z"
                except Exception:
                    ts = None
                rows.append({
                    "added_timestamp": ts,
                    "title": title.strip(),
                    "url": url,
                    "folder_path": "Root"
                })
    if rows:
        table_id = f"{GCP_PROJECT}.{BQ_DATASET}.takeout_chrome_bookmarks"
        print(f"[BOOKMARKS] Loading {len(rows)} bookmarks to {table_id}...")
        job_config = bigquery.LoadJobConfig(write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE)
        job = bq_client.load_table_from_json(rows, table_id, job_config=job_config)
        job.result()
        print("[✓] Bookmarks Ingested Successfully!")
    else:
        print("[!] No bookmarks found.")

def parse_and_load_locations(bq_client, local_zip_path, inner_path):
    print(f"[LOCATION] Parsing location records from local ZIP...")
    rows = []
    table_id = f"{GCP_PROJECT}.{BQ_DATASET}.takeout_location_history"
    
    with zipfile.ZipFile(local_zip_path) as z:
        with z.open(inner_path) as f:
            content = f.read().decode("utf-8", errors="ignore")
            data = json.loads(content)
            locations = data.get("locations", [])
            print(f"[LOCATION] Found {len(locations)} location records.")
            
            for item in locations:
                lat = item.get("latitudeE7")
                lon = item.get("longitudeE7")
                ts_ms = item.get("timestampMs")
                ts = item.get("timestamp")
                acc = item.get("accuracy")
                vel = item.get("velocity")
                alt = item.get("altitude")
                
                if lat is not None and lon is not None:
                    lat_val = lat / 10000000.0
                    lon_val = lon / 10000000.0
                    
                    parsed_ts = None
                    if ts_ms:
                        try:
                            parsed_ts = datetime.datetime.utcfromtimestamp(int(ts_ms) / 1000.0).isoformat() + "Z"
                        except Exception:
                            pass
                    elif ts:
                        parsed_ts = ts
                        
                    if parsed_ts:
                        rows.append({
                            "timestamp": parsed_ts,
                            "latitude": lat_val,
                            "longitude": lon_val,
                            "accuracy": acc,
                            "velocity": vel,
                            "altitude": alt
                        })
                        
                # Batch load
                if len(rows) >= 15000:
                    print(f"[LOCATION] Loading batch of {len(rows)} records to BigQuery...")
                    job_config = bigquery.LoadJobConfig(write_disposition=bigquery.WriteDisposition.WRITE_APPEND)
                    job = bq_client.load_table_from_json(rows, table_id, job_config=job_config)
                    job.result()
                    rows = []
                    
            if rows:
                print(f"[LOCATION] Loading final batch of {len(rows)} records to BigQuery...")
                job_config = bigquery.LoadJobConfig(write_disposition=bigquery.WriteDisposition.WRITE_APPEND)
                job = bq_client.load_table_from_json(rows, table_id, job_config=job_config)
                job.result()
                
            print(f"[✓] Location History Ingestion Complete!")

def main():
    with open("C:\\OsintNeoAi\\takeout_scan_results.json", "r") as f:
        scan_results = json.load(f)
        
    print("[PIPELINE] Initializing BigQuery client...")
    bq_client = bigquery.Client(project=GCP_PROJECT)
    ensure_tables(bq_client)
    
    if "Bookmarks.html" in scan_results and "Records.json" in scan_results:
        bm_res = scan_results["Bookmarks.html"]
        loc_res = scan_results["Records.json"]
        
        # Both are inside the same ZIP: takeout-20230501T063814Z-001.zip
        zip_name = bm_res["zip"]
        local_zip = download_zip(zip_name)
        
        parse_and_load_bookmarks(bq_client, local_zip, bm_res["path_in_zip"])
        parse_and_load_locations(bq_client, local_zip, loc_res["path_in_zip"])
        
        # Clean up local zip file
        try:
            os.remove(local_zip)
            print("[CLEANUP] Removed temporary ZIP file.")
        except Exception as e:
            print(f"[CLEANUP] Failed to remove ZIP: {e}")

if __name__ == "__main__":
    main()
