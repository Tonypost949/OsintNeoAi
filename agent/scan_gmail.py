"""
scan_gmail.py — Gmail Scanner for OSINTNeoAi
====================================================
Scans the authenticated user's Gmail inbox, catalogues emails,
and ingests the metadata into BigQuery for forensic cross-referencing.

Target table: project-743aab84-f9a5-4ec7-954.national_audits.gmail_index
"""

import os
import sys
import json
import datetime
from typing import List, Dict, Any

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
BQ_TABLE = "gmail_index"
FULL_TABLE_ID = f"{GCP_PROJECT}.{BQ_DATASET}.{BQ_TABLE}"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRET_FILE = os.path.join(SCRIPT_DIR, "client_secret.json")
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token_gmail.json") # Use a separate token file for Gmail

# Gmail API scopes — read-only
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# ---------------------------------------------------------------------------
# AUTH — Custom OAuth Desktop Flow
# ---------------------------------------------------------------------------
def get_gmail_service():
    """
    Build a Gmail v1 service using a custom OAuth 2.0 Desktop client.
    Tokens are cached in token_gmail.json for reuse across runs.
    """
    creds = None

    # Load cached token if it exists
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If no valid creds, run the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("[AUTH] Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("[AUTH] Launching OAuth consent flow in browser...")
            print(f"[AUTH] Using client: {CLIENT_SECRET_FILE}")
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Cache the token for future runs
        with open(TOKEN_FILE, "w") as token_file:
            token_file.write(creds.to_json())
        print("[AUTH] Token saved for future use.\n")

    service = build("gmail", "v1", credentials=creds)
    return service

# ---------------------------------------------------------------------------
# SCAN
# ---------------------------------------------------------------------------
def get_header(headers: List[Dict[str, str]], name: str) -> str:
    for h in headers:
        if h['name'].lower() == name.lower():
            return h['value']
    return ""

def scan_gmail(service, max_results=5000):
    """
    Iterates through the authenticated user's Gmail.
    Returns a list of dicts with email metadata.
    Note: Gmail can be huge, so we limit to max_results initially to avoid running forever,
    but we'll paginate through as many as we can within that limit.
    """
    all_messages = []
    page_token = None
    page_num = 0

    print("[GMAIL SCAN] Starting Gmail enumeration (metadata only)...")

    while True:
        page_num += 1
        results = (
            service.users().messages()
            .list(
                userId="me",
                maxResults=500, # Gmail API max per page
                pageToken=page_token,
                includeSpamTrash=True,
            )
            .execute()
        )

        messages = results.get("messages", [])
        if not messages:
            break

        print(f"  Page {page_num}: fetched {len(messages)} message IDs. Now fetching details...")
        
        # We need to fetch details for each message
        for i, msg in enumerate(messages):
            msg_id = msg['id']
            try:
                # Fetch metadata only to save bandwidth and time
                msg_detail = service.users().messages().get(userId="me", id=msg_id, format="metadata", metadataHeaders=["Subject", "From", "To", "Date"]).execute()
                all_messages.append(msg_detail)
            except Exception as e:
                print(f"    [!] Error fetching message {msg_id}: {e}")
            
            if len(all_messages) % 100 == 0:
                print(f"    ... processed {len(all_messages)} emails ...")

            if len(all_messages) >= max_results:
                break
                
        if len(all_messages) >= max_results:
            print(f"  Reached max_results limit of {max_results}. Stopping early.")
            break

        page_token = results.get("nextPageToken")
        if not page_token:
            break

    print(f"[GMAIL SCAN] Complete. {len(all_messages)} emails catalogued.\n")
    return all_messages

# ---------------------------------------------------------------------------
# TRANSFORM
# ---------------------------------------------------------------------------
def transform_for_bq(raw_messages):
    """
    Converts raw Gmail API responses into BigQuery-friendly rows.
    """
    rows = []
    scan_ts = datetime.datetime.utcnow().isoformat() + "Z"

    for msg in raw_messages:
        payload = msg.get('payload', {})
        headers = payload.get('headers', [])
        
        subject = get_header(headers, 'Subject')
        sender = get_header(headers, 'From')
        recipient = get_header(headers, 'To')
        date_str = get_header(headers, 'Date') # Note: Needs robust parsing in real world, keeping as string for simplicity here
        
        row = {
            "message_id": msg.get("id"),
            "thread_id": msg.get("threadId"),
            "subject": subject,
            "sender": sender,
            "recipient": recipient,
            "date_header": date_str,
            "snippet": msg.get("snippet", ""),
            "label_ids": msg.get("labelIds", []),
            "scan_timestamp": scan_ts,
        }
        rows.append(row)

    return rows

# ---------------------------------------------------------------------------
# BIGQUERY INGEST
# ---------------------------------------------------------------------------
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
    """Create the gmail_index table if it doesn't exist."""
    table_ref = bigquery.Table(FULL_TABLE_ID, schema=BQ_SCHEMA)
    table_ref.description = "Gmail metadata index — OSINTNeoAi forensic scan"

    try:
        bq_client.get_table(FULL_TABLE_ID)
        print(f"[BQ] Table {FULL_TABLE_ID} already exists.")
    except Exception:
        table = bq_client.create_table(table_ref)
        print(f"[BQ] Created table {table.full_table_id}")

def ingest_to_bq(rows):
    """Load scanned Gmail metadata into BigQuery."""
    bq_client = bigquery.Client(project=GCP_PROJECT)

    ensure_table(bq_client)

    job_config = bigquery.LoadJobConfig(
        schema=BQ_SCHEMA,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,  # SAFE APPEND (never truncate)
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    )

    print(f"[BQ] Ingesting {len(rows)} rows into {FULL_TABLE_ID}...")

    load_job = bq_client.load_table_from_json(rows, FULL_TABLE_ID, job_config=job_config)
    load_job.result()  # Wait for completion

    table = bq_client.get_table(FULL_TABLE_ID)
    print(f"[BQ] Done. Table now has {table.num_rows} rows.\n")

# ---------------------------------------------------------------------------
# SUMMARY REPORT
# ---------------------------------------------------------------------------
def print_summary(rows):
    """Print a quick forensic summary of what was found."""
    total = len(rows)
    
    senders = {}
    for r in rows:
        sender = r["sender"]
        if sender:
            senders[sender] = senders.get(sender, 0) + 1

    print("=" * 60)
    print("  OSINT GMAIL SCAN — FORENSIC SUMMARY")
    print("=" * 60)
    print(f"  Total emails catalogued:  {total:,}")
    print()
    print("  TOP 10 SENDERS:")
    for sender, count in sorted(senders.items(), key=lambda x: -x[1])[:10]:
        print(f"    {count:>6,} emails from: {sender[:50]}")
    print("=" * 60)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("  OSINTNeoAi GMAIL SCANNER")
    print(f"  Target:  {FULL_TABLE_ID}")
    print("=" * 60 + "\n")

    # 1. Connect to Gmail (custom OAuth flow)
    service = get_gmail_service()

    # 2. Scan everything
    # Scanning all emails without an artificial limit
    raw_messages = scan_gmail(service, max_results=5000000)

    if not raw_messages:
        print("[!] No emails found. Exiting.")
        return

    # 3. Transform
    rows = transform_for_bq(raw_messages)

    # 4. Print summary
    print_summary(rows)

    # 5. Ingest into BigQuery
    ingest_to_bq(rows)

    print("[✓] Gmail scan complete. Data is now queryable in BigQuery.")
    print(f"    SELECT * FROM `{FULL_TABLE_ID}` ORDER BY scan_timestamp DESC LIMIT 10")


if __name__ == "__main__":
    main()
