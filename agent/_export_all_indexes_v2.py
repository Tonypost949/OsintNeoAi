import subprocess, os, csv, json
from google.cloud import bigquery
from google.oauth2.credentials import Credentials

gcloud = os.path.expanduser(r'~\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd')
token = subprocess.check_output([gcloud, 'auth', 'print-access-token', '--account=txtdjdrop@gmail.com'], shell=True).decode().strip()
creds = Credentials(token=token)
client = bigquery.Client(project='project-743aab84-f9a5-4ec7-954', credentials=creds)
PROJ = "project-743aab84-f9a5-4ec7-954"
BASE = r"C:\migrate opencode\OSINTNEOAI\agent"

def schema_from_sample(table_id):
    sql = f"SELECT * FROM `{table_id}` LIMIT 1"
    job = client.query(sql)
    rows = list(job.result())
    schema = job.schema
    if rows:
        return [f.name for f in schema]
    return [f.name for f in schema] if schema else []

def export_table(table_id, cols, outfile):
    sel = ", ".join([f"`{c}`" for c in cols])
    sql = f"SELECT {sel} FROM `{table_id}`"
    rows = client.query(sql).result()
    with open(outfile, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        cnt = 0
        for r in rows:
            w.writerow([str(getattr(r, c, "")) for c in cols])
            cnt += 1
    return cnt

# OneDrive
od_cols = schema_from_sample(f"{PROJ}.onedrive_forensics.onedrive_documents")
print(f"OneDrive columns ({len(od_cols)}): {od_cols}")
cnt = export_table(f"{PROJ}.onedrive_forensics.onedrive_documents", od_cols, os.path.join(BASE, "onedrive_documents_full.csv"))
print(f"OneDrive exported: {cnt} rows")

# Local scan
ls_cols = schema_from_sample(f"{PROJ}.national_audits.local_scan_file_inventory")
print(f"\nLocal scan columns ({len(ls_cols)}): {ls_cols}")
cnt = export_table(f"{PROJ}.national_audits.local_scan_file_inventory", ls_cols, os.path.join(BASE, "local_scan_inventory.csv"))
print(f"Local scan exported: {cnt} rows")

# All table sizes
for ds in ["national_audits", "onedrive_forensics"]:
    print(f"\n=== {ds} ===")
    for t in client.list_tables(f"{PROJ}.{ds}"):
        tbl = client.get_table(f"{PROJ}.{ds}.{t.table_id}")
        print(f"  {t.table_id}: {tbl.num_rows} rows, {len(tbl.schema)} cols")
