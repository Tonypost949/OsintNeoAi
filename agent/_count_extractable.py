import subprocess, os, io, time, sys
from google.cloud import bigquery
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

GCLOUD = os.path.expanduser(r'~\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd')
PROJ = "project-743aab84-f9a5-4ec7-954"

def get_clients():
    token = subprocess.check_output([GCLOUD, 'auth', 'print-access-token', '--account=txtdjdrop@gmail.com'], shell=True).decode().strip()
    creds = Credentials(token=token)
    return bigquery.Client(project=PROJ, credentials=creds), creds

def get_drive_service():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from auth_helper import authenticate
    creds = authenticate("Drive", ["https://www.googleapis.com/auth/drive.readonly"], "token_drive.json")
    return build("drive", "v3", credentials=creds)

bq, _ = get_clients()
drive = get_drive_service()

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
        SchemaField("extracted_text", "STRING"),
        SchemaField("extract_timestamp", "TIMESTAMP"),
    ]
    bq.create_table(Table(TEXT_TABLE, schema=schema))
    print(f"Created {TEXT_TABLE}")

# Count what's NOT yet processed
sql = f"""
SELECT COUNT(*) as cnt
FROM `{PROJ}.national_audits.drive_file_index` d
LEFT JOIN `{PROJ}.national_audits.drive_extracted_text` e ON d.file_id = e.file_id
WHERE e.file_id IS NULL
  AND d.mime_type NOT LIKE 'application/vnd.google-apps.folder'
  AND d.mime_type NOT LIKE 'video/%%'
  AND d.mime_type NOT LIKE 'image/%%'
  AND d.mime_type NOT LIKE 'audio/%%'
  AND d.mime_type NOT LIKE 'application/octet-stream'
"""
r = list(bq.query(sql).result())[0]
print(f"Files to extract: {r.cnt}")

# Get extractable MIME breakdown
sql = f"""
SELECT d.mime_type, COUNT(*) as cnt
FROM `{PROJ}.national_audits.drive_file_index` d
LEFT JOIN `{PROJ}.national_audits.drive_extracted_text` e ON d.file_id = e.file_id
WHERE e.file_id IS NULL
  AND d.mime_type NOT LIKE 'application/vnd.google-apps.folder'
  AND d.mime_type NOT LIKE 'video/%%'
  AND d.mime_type NOT LIKE 'image/%%'
  AND d.mime_type NOT LIKE 'audio/%%'
  AND d.mime_type NOT LIKE 'application/octet-stream'
GROUP BY d.mime_type ORDER BY cnt DESC LIMIT 15
"""
print("Top MIME types to extract:")
for r in bq.query(sql).result():
    print(f"  {r.mime_type}: {r.cnt}")
