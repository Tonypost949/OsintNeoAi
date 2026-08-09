import subprocess, os
from google.cloud import bigquery
from google.oauth2.credentials import Credentials
gcloud = os.path.expanduser(r'~\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd')
token = subprocess.check_output([gcloud, 'auth', 'print-access-token', '--account=txtdjdrop@gmail.com'], shell=True).decode().strip()
creds = Credentials(token=token)
client = bigquery.Client(project='project-743aab84-f9a5-4ec7-954', credentials=creds)
PROJ = "project-743aab84-f9a5-4ec7-954"

# MIME types
sql = f"SELECT mime_type, COUNT(*) as cnt FROM `{PROJ}.national_audits.drive_file_index` GROUP BY mime_type ORDER BY cnt DESC LIMIT 20"
print("Top MIME types:")
for r in client.query(sql).result():
    print(f"  {r.mime_type or 'N/A'}: {r.cnt}")

# Unique file count
sql = f"SELECT COUNT(DISTINCT file_id) as uniq FROM `{PROJ}.national_audits.drive_file_index`"
r = list(client.query(sql).result())[0]
print(f"\nUnique file_ids: {r.uniq}")
