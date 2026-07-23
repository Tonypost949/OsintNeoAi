import subprocess, os
from google.cloud import bigquery
from google.oauth2.credentials import Credentials
gcloud = os.path.expanduser(r'~\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd')
token = subprocess.check_output([gcloud, 'auth', 'print-access-token', '--account=txtdjdrop@gmail.com'], shell=True).decode().strip()
creds = Credentials(token=token)
client = bigquery.Client(project='project-743aab84-f9a5-4ec7-954', credentials=creds)
PROJ = "project-743aab84-f9a5-4ec7-954"

# Deduplicate keeping latest scan_timestamp per file_id
sql = f"""
CREATE OR REPLACE TABLE `{PROJ}.national_audits.drive_file_index`
AS
SELECT * EXCEPT(rn) FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY file_id ORDER BY scan_timestamp DESC) as rn
  FROM `{PROJ}.national_audits.drive_file_index`
)
WHERE rn = 1
"""
print("Deduplicating by file_id...")
client.query(sql).result()
print("Done")

r = list(client.query(f"SELECT COUNT(*) as cnt FROM `{PROJ}.national_audits.drive_file_index`").result())[0]
print(f"Unique count: {r.cnt} rows")
