import subprocess, os, csv
from google.cloud import bigquery
from google.oauth2.credentials import Credentials

gcloud = os.path.expanduser(r'~\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd')
token = subprocess.check_output([gcloud, 'auth', 'print-access-token', '--account=txtdjdrop@gmail.com'], shell=True).decode().strip()
creds = Credentials(token=token)
client = bigquery.Client(project='project-743aab84-f9a5-4ec7-954', credentials=creds)

PROJ = "project-743aab84-f9a5-4ec7-954"
BASE = r"C:\migrate opencode\OSINTNEOAI\agent"

# OneDrive
sql = f"SELECT * FROM `{PROJ}.onedrive_forensics.onedrive_documents` ORDER BY file_name"
rows = client.query(sql).result()
with open(os.path.join(BASE, "onedrive_documents_full.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    cols = [f.name for f in rows.schema]
    w.writerow(cols)
    cnt = 0
    for r in rows:
        w.writerow([str(getattr(r, c, "")) for c in cols])
        cnt += 1
print(f"OneDrive: {cnt} rows")

# local_scan_file_inventory
sql = f"SELECT column_name, data_type FROM `{PROJ}.INFORMATION_SCHEMA.COLUMNS` WHERE table_name = 'local_scan_file_inventory'"
cols = list(client.query(sql).result())
print("\nlocal_scan_file_inventory columns:")
for c in cols:
    print(f"  {c.column_name}: {c.data_type}")

sql = f"SELECT * FROM `{PROJ}.national_audits.local_scan_file_inventory` ORDER BY file_path LIMIT 10"
rows = list(client.query(sql).result())
print("\nSample local files:")
for r in rows:
    print(dict(r))
