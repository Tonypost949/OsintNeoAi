import subprocess, os, csv
from google.cloud import bigquery
from google.oauth2.credentials import Credentials

gcloud = os.path.expanduser(r'~\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd')
token = subprocess.check_output([gcloud, 'auth', 'print-access-token', '--account=txtdjdrop@gmail.com'], shell=True).decode().strip()
creds = Credentials(token=token)
client = bigquery.Client(project='project-743aab84-f9a5-4ec7-954', credentials=creds)
PROJ = "project-743aab84-f9a5-4ec7-954"
BASE = r"C:\migrate opencode\OSINTNEOAI\agent"

# Get schema directly from table metadata
for table_id, outfile in [
    (f"{PROJ}.onedrive_forensics.onedrive_documents", "onedrive_documents_full.csv"),
    (f"{PROJ}.national_audits.local_scan_file_inventory", "local_scan_inventory.csv"),
    (f"{PROJ}.national_audits.local_scan_extracted_text", "local_scan_extracted_text.csv"),
]:
    tbl = client.get_table(table_id)
    cols = [f.name for f in tbl.schema]
    print(f"{table_id.split('.')[-1]}: {tbl.num_rows} rows, {len(cols)} cols -> {outfile}")
    
    if tbl.num_rows == 0:
        print("  (empty, skipping)")
        continue
    
    # Read in batches to avoid timeout
    sel = ", ".join([f"`{c}`" for c in cols])
    sql = f"SELECT {sel} FROM `{table_id}`"
    
    with open(os.path.join(BASE, outfile), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        cnt = 0
        for row in client.query(sql).result():
            w.writerow([str(getattr(row, c, "")) for c in cols])
            cnt += 1
            if cnt % 5000 == 0:
                print(f"  ... {cnt} rows")
    
    print(f"  Done: {cnt} rows to {outfile}")

# All table summary
for ds in ["national_audits", "onedrive_forensics"]:
    print(f"\n=== {ds} ===")
    for t in client.list_tables(f"{PROJ}.{ds}"):
        tbl = client.get_table(f"{PROJ}.{ds}.{t.table_id}")
        print(f"  {t.table_id}: {tbl.num_rows} rows, {len(tbl.schema)} cols")
