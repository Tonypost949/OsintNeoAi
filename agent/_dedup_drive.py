import subprocess, os
from google.cloud import bigquery
from google.oauth2.credentials import Credentials
gcloud = os.path.expanduser(r'~\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd')
token = subprocess.check_output([gcloud, 'auth', 'print-access-token', '--account=txtdjdrop@gmail.com'], shell=True).decode().strip()
creds = Credentials(token=token)
client = bigquery.Client(project='project-743aab84-f9a5-4ec7-954', credentials=creds)
PROJ = "project-743aab84-f9a5-4ec7-954"

# Deduplicate: create new table from distinct rows, swap
sql = f"""
CREATE OR REPLACE TABLE `{PROJ}.national_audits.drive_file_index`
AS SELECT DISTINCT * FROM `{PROJ}.national_audits.drive_file_index`
"""
print("Deduplicating...")
client.query(sql).result()
print("Done")

# Check new count
r = list(client.query(f"SELECT COUNT(*) as cnt FROM `{PROJ}.national_audits.drive_file_index`").result())[0]
print(f"New count: {r.cnt} rows")
