import subprocess, os, io, time, sys, concurrent.futures, threading
from google.cloud import bigquery
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

GCLOUD = os.path.expanduser(r'~\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd')
PROJ = "project-743aab84-f9a5-4ec7-954"
TEXT_TABLE = f"{PROJ}.national_audits.drive_extracted_text"
LOCK = threading.Lock()
PROGRESS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extract_progress.txt")

# Only truly text-extractable MIME types
TEXT_MIMES = [
    "text/", "application/pdf", "application/json", "application/xml",
    "application/msword", "application/vnd.openxmlformats-officedocument",
    "application/vnd.google-apps.document", "application/vnd.google-apps.spreadsheet",
    "application/rtf", "application/x-yaml", "application/x-sh",
    "application/javascript", "text/javascript",
]

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

def download_and_extract(file_id, file_name, mime_type, web_view_link):
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
        data = fh.getvalue()
        return file_id, file_name, mime_type, web_view_link, data, None
    except Exception as e:
        return file_id, file_name, mime_type, web_view_link, None, str(e)

def extract_text(data, mime_type):
    try:
        # PDF
        if mime_type == "application/pdf":
            try:
                import fitz
                doc = fitz.open(stream=data, filetype="pdf")
                text = "\n".join([page.get_text() for page in doc])
                doc.close()
                return text[:50000]
            except ImportError:
                pass
        # Word docs
        if "word" in mime_type.lower() or "officedocument" in mime_type.lower():
            try:
                import docx2txt
                return docx2txt.process(io.BytesIO(data))[:50000]
            except ImportError:
                pass
        # Everything else: text decode
        return data.decode("utf-8", errors="replace")[:50000]
    except:
        return ""

# Read last position
last_id = ""
if os.path.exists(PROGRESS_FILE):
    with open(PROGRESS_FILE) as f:
        last_id = f.read().strip()

mime_conditions = " OR ".join([f"d.mime_type LIKE '{m}%'" for m in [
    "text/", "application/pdf", "application/json", "application/xml",
    "application/msword", "application/vnd.openxmlformats-officedocument",
    "application/vnd.google-apps.document", "application/vnd.google-apps.spreadsheet",
    "application/rtf", "application/javascript", "text/javascript",
]])
sql = f"""
SELECT d.file_id, d.file_name, d.mime_type, d.web_view_link
FROM `{PROJ}.national_audits.drive_file_index` d
LEFT JOIN `{PROJ}.national_audits.drive_extracted_text` e ON d.file_id = e.file_id
WHERE e.file_id IS NULL
  AND ({mime_conditions})
ORDER BY d.modified_time DESC
"""

rows = list(bq.query(sql).result())
if not rows:
    print("No more files to extract!")
    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)
    sys.exit(0)

print(f"{len(rows)} files remaining. Extracting with 5 parallel workers...")

bq_rows = []
processed = 0

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = []
    for r in rows:
        futures.append(executor.submit(download_and_extract, r.file_id, r.file_name, r.mime_type, r.web_view_link))
    
    for i, future in enumerate(concurrent.futures.as_completed(futures)):
        fid, fname, mime, link, data, err = future.result()
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        
        if err:
            bq_rows.append({"file_id": fid, "file_name": fname, "mime_type": mime,
                           "web_view_link": link, "extracted_text": "", "extract_timestamp": ts})
        else:
            text = extract_text(data, mime)
            bq_rows.append({"file_id": fid, "file_name": fname, "mime_type": mime,
                           "web_view_link": link, "extracted_text": text, "extract_timestamp": ts})
        
        processed += 1
        
        if len(bq_rows) >= 50 or processed == len(rows):
            for attempt in range(3):
                try:
                    bq.load_table_from_json(bq_rows, TEXT_TABLE,
                        job_config=bigquery.LoadJobConfig(write_disposition=bigquery.WriteDisposition.WRITE_APPEND)
                    ).result()
                    break
                except:
                    if attempt < 2:
                        bq = get_bq()
                    else:
                        print(f"  BQ FAIL at {processed}")
            bq_rows = []
        
        if processed % 25 == 0:
            print(f"  {processed}/{len(rows)} done")

print(f"\nExtraction run complete: {processed} files")
