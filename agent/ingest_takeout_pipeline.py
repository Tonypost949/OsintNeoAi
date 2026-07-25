import os
import sys
import json
import datetime
import subprocess
from google.cloud import bigquery

sys.stdout.reconfigure(encoding="utf-8")

GCP_PROJECT = os.environ.get("GOOGLE_PROJECT_ID", "project-743aab84-f9a5-4ec7-954")
BQ_DATASET = "national_audits"
CHROME_HISTORY_TABLE = "takeout_chrome_history"
FULL_CHROME_TABLE_ID = f"{GCP_PROJECT}.{BQ_DATASET}.{CHROME_HISTORY_TABLE}"

def ensure_chrome_table(bq_client):
    schema = [
        bigquery.SchemaField("visit_time", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("title", "STRING"),
        bigquery.SchemaField("url", "STRING"),
        bigquery.SchemaField("visit_transition", "STRING"),
        bigquery.SchemaField("ingest_timestamp", "TIMESTAMP")
    ]
    try:
        bq_client.get_table(FULL_CHROME_TABLE_ID)
        print(f"[BQ] Table {FULL_CHROME_TABLE_ID} already exists.")
    except Exception:
        table_ref = bigquery.Table(FULL_CHROME_TABLE_ID, schema=schema)
        table_ref.description = "Chrome browser history ingested from Google Takeout"
        bq_client.create_table(table_ref)
        print(f"[BQ] Created table {FULL_CHROME_TABLE_ID}.")

def ingest_chrome_history():
    print("[CHROME] Initializing BigQuery Client...")
    bq_client = bigquery.Client(project=GCP_PROJECT)
    ensure_chrome_table(bq_client)
    
    remote_path = "gdrive:Sharedall/takeouts all 22226/Takeout/Chrome/History.json"
    print(f"[CHROME] Streaming {remote_path} via Rclone...")
    
    cmd = ["rclone", "cat", remote_path]
    res = subprocess.run(cmd, capture_output=True, check=True)
    
    print("[CHROME] Parsing JSON content...")
    data = json.loads(res.stdout.decode('utf-8', errors='ignore'))
    history_items = data.get("Browser History", [])
    print(f"[CHROME] Found {len(history_items)} history items to process.")
    
    rows_to_insert = []
    scan_ts = datetime.datetime.utcnow().isoformat() + "Z"
    
    for item in history_items:
        # time_usec is microseconds since Epoch
        usec = item.get("time_usec", 0)
        timestamp = datetime.datetime.utcfromtimestamp(usec / 1000000.0).isoformat() + "Z"
        
        row = {
            "visit_time": timestamp,
            "title": item.get("title"),
            "url": item.get("url"),
            "visit_transition": item.get("page_transition_qualifier"),
            "ingest_timestamp": scan_ts
        }
        rows_to_insert.append(row)
        
    if rows_to_insert:
        print(f"[CHROME] Loading {len(rows_to_insert)} rows to {FULL_CHROME_TABLE_ID}...")
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
        )
        job = bq_client.load_table_from_json(rows_to_insert, FULL_CHROME_TABLE_ID, job_config=job_config)
        job.result()
        print("[✓] Chrome History Ingestion Complete!")
    else:
        print("[!] No records found to load.")

if __name__ == "__main__":
    ingest_chrome_history()
