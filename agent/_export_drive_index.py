import subprocess, os, csv
from google.cloud import bigquery
from google.oauth2.credentials import Credentials

gcloud = os.path.expanduser(r'~\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd')
token = subprocess.check_output([gcloud, 'auth', 'print-access-token', '--account=txtdjdrop@gmail.com'], shell=True).decode().strip()
creds = Credentials(token=token)
client = bigquery.Client(project='project-743aab84-f9a5-4ec7-954', credentials=creds)

PROJ = "project-743aab84-f9a5-4ec7-954"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "drive_file_index_full.csv")

sql = f"""
SELECT file_id, file_name, mime_type, web_view_link, size_bytes, created_time, modified_time, is_shared, is_trashed
FROM `{PROJ}.national_audits.drive_file_index`
ORDER BY file_name
"""

rows = client.query(sql).result()
count = 0
with open(OUT, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["file_id", "file_name", "mime_type", "web_view_link", "size_bytes", "created_time", "modified_time", "is_shared", "is_trashed"])
    for r in rows:
        writer.writerow([r.file_id, r.file_name, r.mime_type, r.web_view_link, r.size_bytes, str(r.created_time) if r.created_time else "", str(r.modified_time) if r.modified_time else "", r.is_shared, r.is_trashed])
        count += 1

print(f"Exported {count} rows to {OUT}")
