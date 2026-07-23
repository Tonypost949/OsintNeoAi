import subprocess, os, io, time, sys, json
from google.cloud import bigquery, storage
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

GCLOUD = os.path.expanduser(r'~\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd')
PROJ = "project-743aab84-f9a5-4ec7-954"
BUCKET = "backup-project-743aab84-f9a5-4ec7-954"

def get_clients():
    token = subprocess.check_output([GCLOUD, 'auth', 'print-access-token', '--account=txtdjdrop@gmail.com'], shell=True).decode().strip()
    creds = Credentials(token=token)
    bq = bigquery.Client(project=PROJ, credentials=creds)
    stg = storage.Client(project=PROJ, credentials=creds)
    return bq, stg, creds

def get_drive_service():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from auth_helper import authenticate
    creds = authenticate("Drive", ["https://www.googleapis.com/auth/drive.readonly"], "token_drive.json")
    return build("drive", "v3", credentials=creds)

bq, stg, _ = get_clients()
drive = get_drive_service()
bucket = stg.bucket(BUCKET)

TEXT_TABLE = f"{PROJ}.national_audits.drive_extracted_text"
try:
    bq.get_table(TEXT_TABLE)
except:
    from google.cloud.bigquery import SchemaField, Table
    schema = [
        SchemaField("file_id", "STRING"),
        SchemaField("file_name", "STRING"),
        SchemaField("mime_type", "STRING"),
        SchemaField("web_view_link", "STRING"),
        SchemaField("gcs_path", "STRING"),
        SchemaField("extracted_text", "STRING"),
        SchemaField("extract_timestamp", "TIMESTAMP"),
    ]
    bq.create_table(Table(TEXT_TABLE, schema=schema))
    print(f"Created {TEXT_TABLE}")

EXTRACTABLE_MIMES = [
    "text/", "application/pdf", "application/json", "application/xml",
    "application/msword", "application/vnd.openxmlformats-officedocument",
    "application/vnd.google-apps.document", "application/vnd.google-apps.spreadsheet",
    "application/vnd.google-apps.presentation", "application/rtf",
    "application/x-yaml", "application/x-sh",
]

def should_extract(mime):
    return any(mime.startswith(p) for p in EXTRACTABLE_MIMES)

def download_file(file_id, mime_type, file_name):
    fname = "".join(c if c.isalnum() or c in ".-_ " else "_" for c in (file_name or f"file_{file_id}"))[:100]
    try:
        if mime_type.startswith("application/vnd.google-apps"):
            export_mime = "text/plain"
            if "spreadsheet" in mime_type: export_mime = "text/csv"
            request = drive.files().export_media(fileId=file_id, mimeType=export_mime)
        else:
            request = drive.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        fh.seek(0)
        return fh.read(), fname, None
    except Exception as e:
        return None, fname, str(e)

# Process in chunks of 50 files
CHUNK = 50
BQ_REFRESH_EVERY = 10
bq_batch_count = 0
skip_existing = True

# Get files not yet in extracted_text table
sql = f"""
SELECT d.file_id, d.file_name, d.mime_type, d.web_view_link
FROM `{PROJ}.national_audits.drive_file_index` d
LEFT JOIN `{PROJ}.national_audits.drive_extracted_text` e ON d.file_id = e.file_id
WHERE e.file_id IS NULL
  AND d.mime_type NOT LIKE 'application/vnd.google-apps.folder'
ORDER BY d.modified_time DESC
LIMIT {CHUNK}
"""
rows = list(bq.query(sql).result())
if not rows:
    print("No more files to process!")
    sys.exit(0)

print(f"Processing {len(rows)} files...")
success = 0
fail = 0

for i, r in enumerate(rows):
    bq_batch_count += 1
    if bq_batch_count % BQ_REFRESH_EVERY == 0:
        # Refresh token
        _, _, creds = get_clients()
    
    data, fname, err = download_file(r.file_id, r.mime_type, r.file_name)
    if err:
        print(f"[{i+1}] {r.file_name}: FAIL - {err}")
        fail += 1
        continue
    
    gcs_key = f"drive_content/{r.file_id}/{fname}"
    try:
        bucket.blob(gcs_key).upload_from_string(data)
    except Exception as e:
        print(f"[{i+1}] {r.file_name}: GCS FAIL - {e}")
        fail += 1
        continue
    
    text = data.decode("utf-8", errors="replace")[:50000] if should_extract(r.mime_type) else ""
    bq.load_table_from_json([{
        "file_id": r.file_id, "file_name": r.file_name, "mime_type": r.mime_type,
        "web_view_link": r.web_view_link, "gcs_path": f"gs://{BUCKET}/{gcs_key}",
        "extracted_text": text, "extract_timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
    }], TEXT_TABLE, job_config=bigquery.LoadJobConfig(write_disposition=bigquery.WriteDisposition.WRITE_APPEND)).result()
    
    success += 1
    if i % 10 == 9:
        print(f"  [{i+1}] ... {success} success, {fail} fail")

print(f"\nDone: {success} success, {fail} failed this run")
