import subprocess, os, io, time, sys
from google.cloud import bigquery
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

GCLOUD = os.path.expanduser(r'~\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd')
PROJ = "project-743aab84-f9a5-4ec7-954"

def get_bq():
    token = subprocess.check_output([GCLOUD, 'auth', 'print-access-token', '--account=txtdjdrop@gmail.com'], shell=True).decode().strip()
    return bigquery.Client(project=PROJ, credentials=Credentials(token=token))

def get_drive():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from auth_helper import authenticate
    creds = authenticate("Drive", ["https://www.googleapis.com/auth/drive.readonly"], "token_drive.json")
    return build("drive", "v3", credentials=creds)

bq = get_bq()
drive = get_drive()

TEXT_TABLE = f"{PROJ}.national_audits.drive_extracted_text"
# Ensure table
try:
    bq.get_table(TEXT_TABLE)
except:
    from google.cloud.bigquery import SchemaField, Table
    schema = [
        SchemaField("file_id", "STRING"),
        SchemaField("file_name", "STRING"),
        SchemaField("mime_type", "STRING"),
        SchemaField("web_view_link", "STRING"),
        SchemaField("extracted_text", "STRING"),
        SchemaField("extract_timestamp", "TIMESTAMP"),
    ]
    bq.create_table(Table(TEXT_TABLE, schema=schema))

# MIME types that are text-extractable via simple decode
SIMPLE_TEXT = [
    "text/", "application/json", "application/xml", "application/x-yaml",
    "application/x-sh", "application/javascript", "application/x-python-code",
    "application/x-python", "application/x-bash",
]

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

def extract_text(data, mime_type):
    try:
        # Simple text/code files
        if any(mime_type.startswith(p) for p in SIMPLE_TEXT):
            return data.decode("utf-8", errors="replace")[:50000]
        # Try PDF with PyMuPDF
        if mime_type == "application/pdf":
            try:
                import fitz
                doc = fitz.open(stream=data, filetype="pdf")
                text = "\n".join([page.get_text() for page in doc])
                doc.close()
                return text[:50000]
            except ImportError:
                return data.decode("utf-8", errors="replace")[:50000]
        # Try Word
        if "word" in mime_type.lower() or "officedocument" in mime_type.lower():
            try:
                import docx2txt
                return docx2txt.process(io.BytesIO(data))[:50000]
            except ImportError:
                # Fallback: try binary decode
                return data.decode("utf-8", errors="replace")[:50000]
        # CSV, generic text fallback
        if mime_type.startswith("application/") and "zip" not in mime_type and "dosexec" not in mime_type:
            try:
                return data.decode("utf-8", errors="replace")[:50000]
            except:
                pass
    except:
        pass
    return ""

# Batch size per run
CHUNK = 500
BQ_REFRESH_EVERY = 20
batch_count = 0

sql = f"""
SELECT d.file_id, d.file_name, d.mime_type, d.web_view_link
FROM `{PROJ}.national_audits.drive_file_index` d
LEFT JOIN `{PROJ}.national_audits.drive_extracted_text` e ON d.file_id = e.file_id
WHERE e.file_id IS NULL
  AND d.mime_type NOT LIKE 'application/vnd.google-apps.folder'
  AND d.mime_type NOT LIKE 'video/%%'
  AND d.mime_type NOT LIKE 'image/%%'
  AND d.mime_type NOT LIKE 'audio/%%'
  AND d.mime_type NOT LIKE 'application/octet-stream'
  AND d.mime_type NOT LIKE 'application/x-dosexec'
  AND d.mime_type NOT LIKE 'application/x-msdownload'
  AND d.mime_type NOT LIKE 'application/x-zip'
ORDER BY d.modified_time DESC
LIMIT {CHUNK}
"""

rows = list(bq.query(sql).result())
if not rows:
    print("No more files to extract!")
    sys.exit(0)

print(f"Extracting {len(rows)} files...")
success = 0
fail = 0
bq_rows = []

def flush_bq(bq_client):
    global bq_rows
    if not bq_rows:
        return
    for attempt in range(3):
        try:
            bq_client.load_table_from_json(bq_rows, TEXT_TABLE,
                job_config=bigquery.LoadJobConfig(write_disposition=bigquery.WriteDisposition.WRITE_APPEND)
            ).result()
            break
        except Exception as e:
            if attempt < 2:
                print(f"  [BQ RETRY] {e}")
                bq_client = get_bq()
            else:
                print(f"  [BQ FAIL] {e}")
                raise
    bq_rows = []

for i, r in enumerate(rows):
    batch_count += 1
    if batch_count % BQ_REFRESH_EVERY == 0:
        bq = get_bq()
        print(f"  [BQ] Refreshed token")

    data, fname, err = download_file(r.file_id, r.mime_type, r.file_name)
    if err:
        bq_rows.append({
            "file_id": r.file_id, "file_name": r.file_name, "mime_type": r.mime_type,
            "web_view_link": r.web_view_link, "extracted_text": "",
            "extract_timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
        })
        fail += 1
    else:
        text = extract_text(data, r.mime_type)
        bq_rows.append({
            "file_id": r.file_id, "file_name": r.file_name, "mime_type": r.mime_type,
            "web_view_link": r.web_view_link, "extracted_text": text,
            "extract_timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
        })
        success += 1

    if len(bq_rows) >= 20 or i == len(rows) - 1:
        flush_bq(bq)

    if i % 20 == 19:
        print(f"  [{i+1}] {success} success, {fail} fail")

flush_bq(bq)
print(f"\nRun complete: {success} extracted, {fail} failed")
