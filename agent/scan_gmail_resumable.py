import os
import sys
import json
import datetime
import time
from typing import List, Dict, Any

sys.stdout.reconfigure(encoding="utf-8")

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.cloud import bigquery

# CONFIG
GCP_PROJECT = os.environ.get("GOOGLE_PROJECT_ID", "project-743aab84-f9a5-4ec7-954")
BQ_DATASET = "national_audits"
BQ_TABLE = "gmail_index"
FULL_TABLE_ID = f"{GCP_PROJECT}.{BQ_DATASET}.{BQ_TABLE}"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRET_FILE = os.path.join(SCRIPT_DIR, "client_secret.json")
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token_gmail.json")
RESUME_TOKEN_FILE = os.path.join(SCRIPT_DIR, "gmail_resume_token.txt")

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_gmail_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token_file:
            token_file.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)

def get_header(headers, name):
    for h in headers:
        if h['name'].lower() == name.lower():
            return h['value']
    return ""

def transform_for_bq(raw_messages):
    rows = []
    scan_ts = datetime.datetime.utcnow().isoformat() + "Z"
    for msg in raw_messages:
        payload = msg.get('payload', {})
        headers = payload.get('headers', [])
        rows.append({
            "message_id": msg.get("id"),
            "thread_id": msg.get("threadId"),
            "subject": get_header(headers, 'Subject'),
            "sender": get_header(headers, 'From'),
            "recipient": get_header(headers, 'To'),
            "date_header": get_header(headers, 'Date'),
            "snippet": msg.get("snippet", ""),
            "label_ids": msg.get("labelIds", []),
            "scan_timestamp": scan_ts,
        })
    return rows

BQ_SCHEMA = [
    bigquery.SchemaField("message_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("thread_id", "STRING"),
    bigquery.SchemaField("subject", "STRING"),
    bigquery.SchemaField("sender", "STRING"),
    bigquery.SchemaField("recipient", "STRING"),
    bigquery.SchemaField("date_header", "STRING"),
    bigquery.SchemaField("snippet", "STRING"),
    bigquery.SchemaField("label_ids", "STRING", mode="REPEATED"),
    bigquery.SchemaField("scan_timestamp", "TIMESTAMP"),
]

def ensure_table(bq_client):
    table_ref = bigquery.Table(FULL_TABLE_ID, schema=BQ_SCHEMA)
    table_ref.description = "Gmail metadata index — OSINTNeoAi forensic scan"
    try:
        bq_client.get_table(FULL_TABLE_ID)
    except Exception:
        bq_client.create_table(table_ref)

def ingest_to_bq(bq_client, rows):
    if not rows: return
    job_config = bigquery.LoadJobConfig(
        schema=BQ_SCHEMA,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    )
    load_job = bq_client.load_table_from_json(rows, FULL_TABLE_ID, job_config=job_config)
    load_job.result()

def scan_gmail_resumable(service, bq_client):
    page_token = None
    if os.path.exists(RESUME_TOKEN_FILE):
        with open(RESUME_TOKEN_FILE, "r") as f:
            page_token = f.read().strip()
            if not page_token: page_token = None

    print(f"[GMAIL SCAN] Resuming from token: {page_token}")
    ensure_table(bq_client)
    
    batch_size = 5000
    current_batch_raw = []
    total_processed = 0
    last_save_time = time.time()

    while True:
        try:
            results = service.users().messages().list(userId="me", maxResults=500, pageToken=page_token, includeSpamTrash=True).execute()
        except Exception as e:
            print(f"[!] Error listing messages: {e}")
            break

        messages = results.get("messages", [])
        if not messages: break

        for msg in messages:
            try:
                msg_detail = service.users().messages().get(userId="me", id=msg['id'], format="metadata", metadataHeaders=["Subject", "From", "To", "Date"]).execute()
                current_batch_raw.append(msg_detail)
            except Exception as e:
                print(f"    [!] Error fetching msg {msg['id']}: {e}")

        page_token = results.get("nextPageToken")
        
        # Check if 10 minutes have passed OR we hit batch size OR no more pages
        if len(current_batch_raw) >= batch_size or not page_token or (time.time() - last_save_time > 600):
            if current_batch_raw:
                rows = transform_for_bq(current_batch_raw)
                ingest_to_bq(bq_client, rows)
                total_processed += len(rows)
                print(f"    ... ingested batch. Total so far in this run: {total_processed}")
            
            # Save token AFTER successful ingest
            if page_token:
                with open(RESUME_TOKEN_FILE, "w") as f:
                    f.write(page_token)
            else:
                if os.path.exists(RESUME_TOKEN_FILE):
                    os.remove(RESUME_TOKEN_FILE) # Clean up when done
            
            current_batch_raw = []
            
            # If triggered by the 10-minute autosave rule, pause for 10 seconds
            if time.time() - last_save_time > 600:
                print("[AUTOSAVE] 10-minute interval reached. Data saved. Pausing for 10 seconds...")
                time.sleep(10)
                last_save_time = time.time()

        if not page_token:
            break

    print(f"[GMAIL SCAN] Complete. Processed {total_processed} emails.")

def main():
    service = get_gmail_service()
    bq_client = bigquery.Client(project=GCP_PROJECT)
    scan_gmail_resumable(service, bq_client)

if __name__ == "__main__":
    main()
