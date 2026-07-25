import os, sys, subprocess, datetime, time, argparse
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from googleapiclient.discovery import build
from google.cloud import bigquery
from google.oauth2.credentials import Credentials

GCP_PROJECT = "project-743aab84-f9a5-4ec7-954"
BQ_DATASET = "national_audits"
BQ_TABLE = "drive_file_index"
FULL_TABLE_ID = f"{GCP_PROJECT}.{BQ_DATASET}.{BQ_TABLE}"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESUME_TOKEN_FILE = os.path.join(SCRIPT_DIR, "drive_resume_token.txt")
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
FILE_FIELDS = "id, name, mimeType, size, createdTime, modifiedTime, owners, sharingUser, shared, webViewLink, parents, trashed, starred, description"

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

GCLOUD = os.path.expanduser(r'~\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd')
BQ_REFRESH_EVERY = 10
_bq_batch_count = 0
_bq_client = None

def get_drive_service():
    from auth_helper import authenticate
    creds = authenticate("Drive", SCOPES, "token_drive.json")
    return build("drive", "v3", credentials=creds)

def get_bq_client():
    global _bq_client
    token = subprocess.check_output([GCLOUD, 'auth', 'print-access-token', '--account=txtdjdrop@gmail.com'], shell=True).decode().strip()
    creds = Credentials(token=token)
    _bq_client = bigquery.Client(project=GCP_PROJECT, credentials=creds)
    return _bq_client

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

def main():
    global _bq_batch_count, _bq_client
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-rows", type=int, default=0, help="Max rows to process this run")
    args = parser.parse_args()
    MAX_ROWS = args.max_rows
    if MAX_ROWS:
        print(f"  Max rows this run: {MAX_ROWS}")
    print("=" * 60)
    print("  OSINTNeoAi GOOGLE DRIVE SCANNER V3 (token refresh)")
    print(f"  Target:  {FULL_TABLE_ID}")
    print("=" * 60 + "\n")

    service = get_drive_service()
    _bq_client = get_bq_client()
    ensure_table(_bq_client)

    page_token = None
    if os.path.exists(RESUME_TOKEN_FILE):
        with open(RESUME_TOKEN_FILE, "r") as f:
            page_token = f.read().strip()
            if page_token:
                print(f"[DRIVE] Resuming from saved token")
            else:
                page_token = None

    batch_size = 2000
    current_batch = []
    total_processed = 0
    scan_ts = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
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
        if MAX_ROWS and (len(current_batch) + total_processed >= MAX_ROWS):
            current_batch = current_batch[:MAX_ROWS - total_processed]

        page_token = results.get("nextPageToken")

        save_now = (len(current_batch) >= batch_size or not page_token or (time.time() - last_save_time > 600))
        if save_now and current_batch:
            _bq_batch_count += 1
            if _bq_batch_count % BQ_REFRESH_EVERY == 0:
                print("  [BQ] Refreshing token...")
                get_bq_client()

            job_config = bigquery.LoadJobConfig(
                schema=BQ_SCHEMA,
                write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
                source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            )
            for attempt in range(3):
                try:
                    _bq_client.load_table_from_json(current_batch, FULL_TABLE_ID, job_config=job_config).result()
                    total_processed += len(current_batch)
                    print(f"  ... Ingested batch of {len(current_batch)}. Total: {total_processed}")
                    break
                except Exception as e:
                    if attempt < 2:
                        print(f"  [RETRY {attempt+1}] BQ load failed, refreshing token...")
                        get_bq_client()
                        time.sleep(2)
                    else:
                        print(f"  [FAIL] BQ load failed after 3 attempts: {e}")
                        if page_token:
                            with open(RESUME_TOKEN_FILE, "w") as f:
                                f.write(page_token)
                            print(f"  Saved resume token")
                        raise

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

    print(f"\n[+] Google Drive Scan Complete! {total_processed} files indexed.")

if __name__ == "__main__":
    main()
