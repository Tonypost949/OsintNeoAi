"""
scan_drive.py — Google Drive Scanner for OSINTNeoAi (Safe Incremental Version)
====================================================
Scans the authenticated user's Google Drive, catalogues every file,
and ingests the metadata into BigQuery for forensic cross-referencing.

Target table: project-743aab84-f9a5-4ec7-954.national_audits.drive_file_index
"""

import os
import sys
import datetime
import time

sys.stdout.reconfigure(encoding="utf-8")

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.cloud import bigquery

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
GCP_PROJECT = os.environ.get("GOOGLE_PROJECT_ID", "project-743aab84-f9a5-4ec7-954")
BQ_DATASET = "national_audits"
BQ_TABLE = "drive_file_index"
FULL_TABLE_ID = f"{GCP_PROJECT}.{BQ_DATASET}.{BQ_TABLE}"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRET_FILE = os.path.join(SCRIPT_DIR, "client_secret.json")
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token.json")
RESUME_TOKEN_FILE = os.path.join(SCRIPT_DIR, "drive_resume_token.txt")

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

FILE_FIELDS = (
    "id, name, mimeType, size, createdTime, modifiedTime, "
    "owners, sharingUser, shared, webViewLink, parents, "
    "trashed, starred, description"
)

# ---------------------------------------------------------------------------
# AUTH
# ---------------------------------------------------------------------------
def get_drive_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("[AUTH] Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("[AUTH] Launching OAuth consent flow in browser...")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token_file:
            token_file.write(creds.to_json())
        print("[AUTH] Token saved.\n")
    return build("drive", "v3", credentials=creds)

# ---------------------------------------------------------------------------
# BIGQUERY SCHEMA
# ---------------------------------------------------------------------------
BQ_SCHEMA = [
    bigquery.SchemaField("file_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("file_name", "STRING"),
    bigquery.SchemaField("mime_type", "STRING"),
    bigquery.SchemaField("size_bytes", "INTEGER"),
    bigquery.SchemaField("created_time", "TIMESTAMP"),
    bigquery.SchemaField("modified_time", "TIMESTAMP"),
    bigquery.SchemaField("owner_emails", "STRING", mode="REPEATED"),
    bigquery.SchemaField("owner_names", "STRING", mode="REPEATED"),
    bigquery.SchemaField("sharing_user_email", "STRING"),
    bigquery.SchemaField("sharing_user_name", "STRING"),
    bigquery.SchemaField("is_shared", "BOOLEAN"),
    bigquery.SchemaField("web_view_link", "STRING"),
    bigquery.SchemaField("parent_folder_ids", "STRING", mode="REPEATED"),
    bigquery.SchemaField("is_trashed", "BOOLEAN"),
    bigquery.SchemaField("is_starred", "BOOLEAN"),
    bigquery.SchemaField("description", "STRING"),
    bigquery.SchemaField("scan_timestamp", "TIMESTAMP"),
]

def ensure_table(bq_client):
    try:
        bq_client.get_table(FULL_TABLE_ID)
    except Exception:
        table_ref = bigquery.Table(FULL_TABLE_ID, schema=BQ_SCHEMA)
        table_ref.description = "Google Drive file index — OSINTNeoAi forensic scan"
        bq_client.create_table(table_ref)

def transform_file(f, scan_ts):
    owners = f.get("owners", [])
    sharing_user = f.get("sharingUser", {})
    return {
        "file_id": f.get("id"),
        "file_name": f.get("name"),
        "mime_type": f.get("mimeType"),
        "size_bytes": int(f["size"]) if f.get("size") else None,
        "created_time": f.get("createdTime"),
        "modified_time": f.get("modifiedTime"),
        "owner_emails": [o.get("emailAddress", "") for o in owners],
        "owner_names": [o.get("displayName", "") for o in owners],
        "sharing_user_email": sharing_user.get("emailAddress"),
        "sharing_user_name": sharing_user.get("displayName"),
        "is_shared": f.get("shared", False),
        "web_view_link": f.get("webViewLink"),
        "parent_folder_ids": f.get("parents", []),
        "is_trashed": f.get("trashed", False),
        "is_starred": f.get("starred", False),
        "description": f.get("description"),
        "scan_timestamp": scan_ts,
    }

# ---------------------------------------------------------------------------
# MAIN SCAN LOOP (INCREMENTAL & SAFE)
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("  OSINTNeoAi GOOGLE DRIVE SCANNER (INCREMENTAL BATCHING)")
    print(f"  Target:  {FULL_TABLE_ID}")
    print("=" * 60 + "\n")

    service = get_drive_service()
    bq_client = bigquery.Client(project=GCP_PROJECT)
    ensure_table(bq_client)

    page_token = None
    if os.path.exists(RESUME_TOKEN_FILE):
        with open(RESUME_TOKEN_FILE, "r") as f:
            page_token = f.read().strip()
            if page_token:
                print(f"[DRIVE] Resuming from saved token: {page_token[:10]}...")
            else:
                page_token = None

    batch_size = 2000
    current_batch = []
    total_processed = 0
    scan_ts = datetime.datetime.utcnow().isoformat() + "Z"
    last_save_time = time.time()

    print("[DRIVE SCAN] Starting enumeration...")

    while True:
        try:
            results = service.files().list(
                pageSize=200,
                fields=f"nextPageToken, files({FILE_FIELDS})",
                pageToken=page_token,
                orderBy="modifiedTime desc",
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
            ).execute()
        except Exception as e:
            print(f"[!] Error fetching files: {e}")
            break

        files = results.get("files", [])
        if not files:
            break

        for f in files:
            current_batch.append(transform_file(f, scan_ts))

        page_token = results.get("nextPageToken")

        # Save condition: Hit batch size OR time limit OR end of pages
        if len(current_batch) >= batch_size or not page_token or (time.time() - last_save_time > 600):
            if current_batch:
                job_config = bigquery.LoadJobConfig(
                    schema=BQ_SCHEMA,
                    write_disposition=bigquery.WriteDisposition.WRITE_APPEND, # SAFE APPEND
                    source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
                )
                bq_client.load_table_from_json(current_batch, FULL_TABLE_ID, job_config=job_config).result()
                
                total_processed += len(current_batch)
                print(f"  ... Ingested batch of {len(current_batch)}. Total processed so far: {total_processed}")
            
            if page_token:
                with open(RESUME_TOKEN_FILE, "w") as f:
                    f.write(page_token)
            else:
                if os.path.exists(RESUME_TOKEN_FILE):
                    os.remove(RESUME_TOKEN_FILE)
            
            current_batch = []
            last_save_time = time.time()

        if not page_token:
            break

    print(f"\n[+] Google Drive Scan Complete! {total_processed} files securely indexed into BigQuery.")

if __name__ == "__main__":
    main()
