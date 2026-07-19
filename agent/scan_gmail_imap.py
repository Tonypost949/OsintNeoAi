"""
scan_gmail_imap.py — Gmail IMAP Scanner for OSINTNeoAi (OAuth Bypass)
========================================================================
Scans Gmail via IMAP using an App Password and streams metadata into BigQuery.
"""

import os
import sys
import json
import imaplib
import email
from email.header import decode_header
import datetime
import re
from google.cloud import bigquery

# Ensure output handles UTF-8
sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
GCP_PROJECT = os.environ.get("GOOGLE_PROJECT_ID", "project-743aab84-f9a5-4ec7-954")
BQ_DATASET = "national_audits"
BQ_TABLE = "gmail_index"
FULL_TABLE_ID = f"{GCP_PROJECT}.{BQ_DATASET}.{BQ_TABLE}"

# Target Email Account
EMAIL_USER = "amd949609@gmail.com"

# ---------------------------------------------------------------------------
# DECODE HEADER HELPER
# ---------------------------------------------------------------------------
def safe_decode(header_val):
    if not header_val:
        return ""
    try:
        decoded_parts = decode_header(header_val)
        result = []
        for text, encoding in decoded_parts:
            if isinstance(text, bytes):
                try:
                    result.append(text.decode(encoding or "utf-8", errors="replace"))
                except Exception:
                    result.append(text.decode("latin1", errors="replace"))
            else:
                result.append(str(text))
        return "".join(result)
    except Exception:
        return str(header_val)

# ---------------------------------------------------------------------------
# BIGQUERY SETUP
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
    table_ref = bigquery.Table(FULL_TABLE_ID, schema=BQ_SCHEMA)
    table_ref.description = "Gmail metadata index — OSINTNeoAi IMAP bypass forensic scan"
    try:
        bq_client.get_table(FULL_TABLE_ID)
        print(f"[BQ] Table {FULL_TABLE_ID} already exists.")
    except Exception:
        table = bq_client.create_table(table_ref)
        print(f"[BQ] Created table {table.full_table_id}")

def ingest_to_bq(rows):
    if not rows:
        print("[BQ] No rows to ingest.")
        return
    bq_client = bigquery.Client(project=GCP_PROJECT)
    ensure_table(bq_client)

    job_config = bigquery.LoadJobConfig(
        schema=BQ_SCHEMA,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    )

    print(f"[BQ] Ingesting {len(rows)} rows into {FULL_TABLE_ID}...")
    load_job = bq_client.load_table_from_json(rows, FULL_TABLE_ID, job_config=job_config)
    load_job.result()
    table = bq_client.get_table(FULL_TABLE_ID)
    print(f"[BQ] Done. Table now has {table.num_rows} rows.\n")

# ---------------------------------------------------------------------------
# IMAP EXTRACTION
# ---------------------------------------------------------------------------
def parse_gmail_extensions(fetch_resp_bytes):
    """
    Parses custom Gmail extensions (X-GM-THRID, X-GM-MSGID) from FETCH response.
    """
    resp_str = fetch_resp_bytes.decode("utf-8", errors="ignore")
    
    # Simple regex to extract X-GM-THRID and X-GM-MSGID
    thrid_match = re.search(r"X-GM-THRID\s+(\d+)", resp_str, re.IGNORECASE)
    msgid_match = re.search(r"X-GM-MSGID\s+(\d+)", resp_str, re.IGNORECASE)
    
    thrid = thrid_match.group(1) if thrid_match else None
    msgid = msgid_match.group(1) if msgid_match else None
    
    return thrid, msgid

def scan_gmail_imap(password, max_results=1000, folder="[Gmail]/All Mail"):
    print(f"[IMAP] Connecting to imap.gmail.com for {EMAIL_USER}...")
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    
    try:
        mail.login(EMAIL_USER, password)
        print("[IMAP] Login successful.")
    except Exception as e:
        print(f"[IMAP] Login failed: {e}")
        sys.exit(1)

    # List mailboxes to verify
    status, mailboxes = mail.list()
    
    # Select folder
    print(f"[IMAP] Selecting folder '{folder}'...")
    status, data = mail.select(folder, readonly=True)
    if status != "OK":
        print(f"[IMAP] Folder '{folder}' not found. Defaulting to 'INBOX'...")
        folder = "INBOX"
        status, data = mail.select(folder, readonly=True)
        if status != "OK":
            print("[IMAP] Failed to select INBOX folder.")
            sys.exit(1)

    print(f"[IMAP] Search all messages in '{folder}'...")
    # Fetch all UIDs
    status, data = mail.uid("search", None, "ALL")
    if status != "OK":
        print("[IMAP] Failed to search messages.")
        sys.exit(1)

    uids = data[0].split()
    total_emails = len(uids)
    print(f"[IMAP] Found {total_emails} messages.")

    # Sort descending (newest first)
    uids.reverse()

    # Limit results
    scan_uids = uids[:max_results]
    print(f"[IMAP] Processing newest {len(scan_uids)} messages...")

    rows = []
    scan_ts = datetime.datetime.utcnow().isoformat() + "Z"

    for idx, uid in enumerate(scan_uids):
        try:
            # Fetch custom Gmail properties along with headers
            status, data = mail.uid("fetch", uid, "(X-GM-THRID X-GM-MSGID BODY.PEEK[HEADER.FIELDS (Message-ID Date From To Subject)])")
            if status != "OK" or not data:
                continue

            raw_envelope = None
            gmail_extension_bytes = b""
            
            for part in data:
                if isinstance(part, tuple):
                    gmail_extension_bytes = part[0]
                    raw_envelope = part[1]
            
            thrid, msgid = parse_gmail_extensions(gmail_extension_bytes)
            
            # If we couldn't parse the message ID via gmail extensions, fall back to UID
            if not msgid:
                msgid = uid.decode()

            # Parse headers
            subject = ""
            sender = ""
            recipient = ""
            date_str = ""
            
            if raw_envelope:
                msg = email.message_from_bytes(raw_envelope)
                subject = safe_decode(msg.get("Subject"))
                sender = safe_decode(msg.get("From"))
                recipient = safe_decode(msg.get("To"))
                date_str = safe_decode(msg.get("Date"))

            # Create row
            row = {
                "message_id": msgid,
                "thread_id": thrid or "",
                "subject": subject,
                "sender": sender,
                "recipient": recipient,
                "date_header": date_str,
                "snippet": f"IMAP Scan - Folder: {folder}",
                "label_ids": [folder],
                "scan_timestamp": scan_ts,
            }
            rows.append(row)
            
            if len(rows) % 100 == 0:
                print(f"  Processed {len(rows)}/{len(scan_uids)} emails...")
                
        except Exception as e:
            print(f"  [!] Error processing UID {uid.decode()}: {e}")

    print(f"[IMAP] Completed extraction. Formatted {len(rows)} rows.")
    mail.logout()
    return rows

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("  OSINTNeoAi GMAIL IMAP SCANNER")
    print(f"  Target:  {FULL_TABLE_ID}")
    print("=" * 60 + "\n")

    # Get App Password
    password = os.environ.get("GMAIL_APP_PASSWORD")
    if not password:
        password = input("Enter GMAIL_APP_PASSWORD for amd949609@gmail.com: ").strip()
    
    if not password:
        print("[!] No password provided. Exiting.")
        sys.exit(1)

    # Perform scan (defaulting to INBOX for quick sync first, can be adjusted)
    rows = scan_gmail_imap(password, max_results=1000, folder="INBOX")

    if not rows:
        print("[!] No messages scanned. Exiting.")
        return

    # Ingest
    ingest_to_bq(rows)
    print("[✓] Gmail IMAP scan complete.")

if __name__ == "__main__":
    main()
