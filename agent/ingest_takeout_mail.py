import os
import sys
import json
import mailbox
import datetime
import subprocess
import zipfile
from email.header import decode_header
from google.cloud import bigquery

sys.stdout.reconfigure(encoding="utf-8")

GCP_PROJECT = os.environ.get("GOOGLE_PROJECT_ID", "project-743aab84-f9a5-4ec7-954")
BQ_DATASET = "national_audits"
TABLE_NAME = "takeout_mail_metadata"
FULL_TABLE_ID = f"{GCP_PROJECT}.{BQ_DATASET}.{TABLE_NAME}"
TEMP_DIR = "G:\\temp_takeout"

def ensure_table(bq_client):
    schema = [
        bigquery.SchemaField("message_id", "STRING"),
        bigquery.SchemaField("sent_timestamp", "TIMESTAMP"),
        bigquery.SchemaField("from_address", "STRING"),
        bigquery.SchemaField("to_addresses", "STRING"),
        bigquery.SchemaField("subject", "STRING")
    ]
    try:
        bq_client.get_table(FULL_TABLE_ID)
        print(f"[BQ] Table {FULL_TABLE_ID} already exists.")
    except Exception:
        table = bigquery.Table(FULL_TABLE_ID, schema=schema)
        bq_client.create_table(table)
        print(f"[BQ] Created table {FULL_TABLE_ID}.")

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

def decode_mime_header(h):
    if not h: return ""
    try:
        decoded_parts = decode_header(h)
        result = ""
        for string, charset in decoded_parts:
            if isinstance(string, bytes):
                result += string.decode(charset or 'utf-8', errors='ignore')
            else:
                result += string
        return result
    except Exception:
        return str(h)

def parse_date(date_str):
    if not date_str: return None
    # Remove timezone names like (PST), (PDT) if they exist
    cleaned_date = re.sub(r'\s*\([^)]*\)', '', date_str)
    # Common email date format parsers
    for fmt in [
        "%a, %d %b %Y %H:%M:%S %z",
        "%d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%Y-%m-%d %H:%M:%S",
    ]:
        try:
            dt = datetime.datetime.strptime(cleaned_date.strip(), fmt)
            return dt.isoformat()
        except Exception:
            pass
    return None

import re

def process_mbox_to_bq(bq_client, mbox_path):
    print(f"[MAIL] Opening and parsing mailbox file {mbox_path}...")
    mb = mailbox.mbox(mbox_path)
    rows = []
    
    for i, msg in enumerate(mb):
        if i % 2000 == 0 and i > 0:
            print(f"[MAIL] Scanned {i} emails...")
            
        msg_id = msg.get('Message-ID', '')
        date_raw = msg.get('Date', '')
        sent_ts = parse_date(date_raw)
        
        row = {
            "message_id": msg_id,
            "sent_timestamp": sent_ts,
            "from_address": decode_mime_header(msg.get('From', '')),
            "to_addresses": decode_mime_header(msg.get('To', '')),
            "subject": decode_mime_header(msg.get('Subject', ''))
        }
        rows.append(row)
        
        if len(rows) >= 10000:
            print(f"[MAIL] Loading batch of {len(rows)} emails to BigQuery...")
            job_config = bigquery.LoadJobConfig(write_disposition=bigquery.WriteDisposition.WRITE_APPEND)
            job = bq_client.load_table_from_json(rows, FULL_TABLE_ID, job_config=job_config)
            job.result()
            rows = []
            
    if rows:
        print(f"[MAIL] Loading final batch of {len(rows)} emails...")
        job_config = bigquery.LoadJobConfig(write_disposition=bigquery.WriteDisposition.WRITE_APPEND)
        job = bq_client.load_table_from_json(rows, FULL_TABLE_ID, job_config=job_config)
        job.result()
        
    print(f"[✓] Email Metadata Ingestion Complete! Loaded emails.")

def main():
    zip_name = "takeout-20230501T063814Z-002.zip"
    inner_path = "Takeout/Mail/All mail Including Spam and Trash.mbox"
    
    print("[PIPELINE] Initializing BigQuery client...")
    bq_client = bigquery.Client(project=GCP_PROJECT)
    ensure_table(bq_client)
    
    local_zip = download_zip(zip_name)
    local_mbox_path = os.path.join(TEMP_DIR, "takeout_mail.mbox")
    
    print(f"[EXTRACT] Extracting {inner_path} from ZIP...")
    with zipfile.ZipFile(local_zip) as z:
        # Save mbox file directly to G:\temp_takeout
        with z.open(inner_path) as z_file:
            with open(local_mbox_path, "wb") as out_file:
                # Chunked write to avoid memory issues
                while True:
                    chunk = z_file.read(1024 * 1024)
                    if not chunk:
                        break
                    out_file.write(chunk)
                    
    print("[EXTRACT] Extraction completed.")
    
    # Process extracted mbox file
    process_mbox_to_bq(bq_client, local_mbox_path)
    
    # Cleanup
    try:
        os.remove(local_zip)
        os.remove(local_mbox_path)
        print("[CLEANUP] Cleaned up temporary files on G: drive.")
    except Exception as e:
        print(f"[CLEANUP] Failed to remove temp files: {e}")

if __name__ == "__main__":
    main()
