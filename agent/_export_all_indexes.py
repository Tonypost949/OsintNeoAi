import subprocess, os, csv
from google.cloud import bigquery
from google.oauth2.credentials import Credentials

gcloud = os.path.expanduser(r'~\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd')
token = subprocess.check_output([gcloud, 'auth', 'print-access-token', '--account=txtdjdrop@gmail.com'], shell=True).decode().strip()
creds = Credentials(token=token)
client = bigquery.Client(project='project-743aab84-f9a5-4ec7-954', credentials=creds)

PROJ = "project-743aab84-f9a5-4ec7-954"
BASE = r"C:\migrate opencode\OSINTNEOAI\agent"

# OneDrive columns
sql = f"SELECT column_name, data_type FROM `{PROJ}.INFORMATION_SCHEMA.COLUMNS` WHERE table_catalog = '{PROJ}' AND table_schema = 'onedrive_forensics' AND table_name = 'onedrive_documents'"
cols = list(client.query(sql).result())
print("OneDrive columns:")
for c in cols:
    print(f"  {c.column_name}: {c.data_type}")

# Export just file_name and any path/url columns
col_names = [c.column_name for c in cols]
path_cols = [c for c in col_names if any(k in c.lower() for k in ["path", "url", "link", "name", "id", "ext", "type", "size", "date", "time"])]
if not path_cols:
    path_cols = col_names[:8]
print(f"\nExporting columns: {path_cols}")
sel = ", ".join([f"`{c}`" for c in path_cols])
sql = f"SELECT {sel} FROM `{PROJ}.onedrive_forensics.onedrive_documents` ORDER BY file_name"

rows = client.query(sql).result()
with open(os.path.join(BASE, "onedrive_documents_index.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(path_cols)
    cnt = 0
    for r in rows:
        w.writerow([str(getattr(r, c, "")) for c in path_cols])
        cnt += 1
print(f"OneDrive exported: {cnt} rows")

# local_scan_file_inventory columns + export
sql = f"SELECT column_name FROM `{PROJ}.INFORMATION_SCHEMA.COLUMNS` WHERE table_name = 'local_scan_file_inventory'"
lcols = [r.column_name for r in client.query(sql).result()]
print(f"\nlocal_scan_file_inventory columns: {lcols}")

sel = ", ".join([f"`{c}`" for c in lcols])
sql = f"SELECT {sel} FROM `{PROJ}.national_audits.local_scan_file_inventory` ORDER BY file_path"
rows = client.query(sql).result()
with open(os.path.join(BASE, "local_scan_inventory.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(lcols)
    cnt = 0
    for r in rows:
        w.writerow([str(getattr(r, c, "")) for c in lcols])
        cnt += 1
print(f"Local scan exported: {cnt} rows")

# List all tables with their sizes
for ds in ["national_audits"]:
    print(f"\n=== {ds} tables ===")
    tables = list(client.list_tables(f"{PROJ}.{ds}"))
    for t in tables:
        tbl = client.get_table(f"{PROJ}.{ds}.{t.table_id}")
        print(f"  {t.table_id}: {tbl.num_rows} rows, {len(tbl.schema)} cols")
