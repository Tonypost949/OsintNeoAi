import subprocess, os
from google.cloud import bigquery
from google.oauth2.credentials import Credentials

gcloud = os.path.expanduser(r'~\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd')
token = subprocess.check_output([gcloud, 'auth', 'print-access-token', '--account=txtdjdrop@gmail.com'], shell=True).decode().strip()
creds = Credentials(token=token)
client = bigquery.Client(project='project-743aab84-f9a5-4ec7-954', credentials=creds)

PROJ = "project-743aab84-f9a5-4ec7-954"

queries = {
    "drive_file_index": f"SELECT COUNT(*) as cnt FROM `{PROJ}.national_audits.drive_file_index`",
    "google_photos_index": f"SELECT COUNT(*) as cnt FROM `{PROJ}.national_audits.google_photos_index`",
    "onedrive_forensics.onedrive_documents": f"SELECT COUNT(*) as cnt FROM `{PROJ}.onedrive_forensics.onedrive_documents`",
}

for name, sql in queries.items():
    try:
        rows = list(client.query(sql).result())
        print(f"{name}: {rows[0].cnt} rows")
    except Exception as e:
        print(f"{name}: ERROR - {e}")

# MIME type breakdown for Drive
sql = f"SELECT mime_type, COUNT(*) as cnt FROM `{PROJ}.national_audits.drive_file_index` GROUP BY mime_type ORDER BY cnt DESC LIMIT 15"
rows = list(client.query(sql).result())
print("\nDrive MIME types:")
for r in rows:
    print(f"  {r.mime_type or 'N/A'}: {r.cnt}")

# Sample file names + URLs
sql = f"SELECT file_name, web_view_link FROM `{PROJ}.national_audits.drive_file_index` WHERE web_view_link IS NOT NULL LIMIT 30"
rows = list(client.query(sql).result())
print("\nSample Drive files:")
for r in rows:
    print(f"  {r.file_name or '?'}")
    if r.web_view_link:
        print(f"    {r.web_view_link}")

# Photos sample
sql = f"SELECT * FROM `{PROJ}.national_audits.google_photos_index` LIMIT 5"
rows = list(client.query(sql).result())
print("\nSample Photos entries (first 5):")
for r in rows:
    print(dict(r))

# All tables in dataset
tables = list(client.list_tables(f"{PROJ}.national_audits"))
print(f"\nAll national_audits tables:")
for t in tables:
    tbl = client.get_table(f"{PROJ}.national_audits.{t.table_id}")
    print(f"  {t.table_id}: {tbl.num_rows} rows")
