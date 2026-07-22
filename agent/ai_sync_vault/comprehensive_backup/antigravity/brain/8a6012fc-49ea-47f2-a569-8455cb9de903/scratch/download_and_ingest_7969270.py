"""
Downloads all 7969270-series EDR files from Google Drive (IronMan DaVinci account)
and stages them to Private_EDR_2025_Real, then ingests a full inventory of all
real EDR files into BigQuery under forensic_layers.real_edr_inventory.
"""

import os
import json
import requests
from google.cloud import bigquery
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import google.auth

DEST_DIR = r"C:\Users\HP\OneDrive\Documents\opencode_work\Private_EDR_2025_Real"
BQ_PROJECT = "project-9c94c2fa-3af4-49f1-a7b"
BQ_DATASET = "forensic_layers"
BQ_TABLE = "real_edr_inventory"
INDEX_PROJECT = "project-743aab84-f9a5-4ec7-954"

os.makedirs(DEST_DIR, exist_ok=True)

# ---- Step 1: Get all 7969270 file IDs from BigQuery ----
print("[1] Querying BigQuery for 7969270 series file IDs...")
index_client = bigquery.Client(project=INDEX_PROJECT)

query = """
SELECT DISTINCT file_name, file_id, size_bytes, web_view_link, created_time, owner_names
FROM `project-743aab84-f9a5-4ec7-954.national_audits_legacy.drive_file_index`
WHERE REGEXP_CONTAINS(file_name, r'^7969270|^79692706|^79692705|^79692707')
  AND mime_type != 'application/vnd.google-apps.folder'
ORDER BY file_name
"""

df_7969270 = index_client.query(query).to_dataframe()
print(f"  Found {len(df_7969270)} files in 7969270 series")

# ---- Step 2: Download each file using ADC credentials ----
print("\n[2] Attempting to download 7969270 files from Google Drive...")
credentials, project = google.auth.default(scopes=["https://www.googleapis.com/auth/drive.readonly"])
credentials.refresh(Request())
token = credentials.token

downloaded = []
failed = []

for _, row in df_7969270.iterrows():
    fname = row["file_name"]
    fid = row["file_id"]
    dest_path = os.path.join(DEST_DIR, fname)

    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
        print(f"  [=] Already exists: {fname}")
        downloaded.append({"file_name": fname, "file_id": fid, "local_path": dest_path, "status": "already_exists"})
        continue

    url = f"https://www.googleapis.com/drive/v3/files/{fid}?alt=media"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        r = requests.get(url, headers=headers, stream=True, timeout=60)
        if r.status_code == 200:
            with open(dest_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024*1024):
                    f.write(chunk)
            size = os.path.getsize(dest_path)
            print(f"  [+] Downloaded: {fname} ({size/1024/1024:.1f}MB)")
            downloaded.append({"file_name": fname, "file_id": fid, "local_path": dest_path, "status": "downloaded", "size_bytes": size})
        else:
            print(f"  [!] Failed {fname}: HTTP {r.status_code} — {r.text[:100]}")
            failed.append({"file_name": fname, "file_id": fid, "error": f"HTTP {r.status_code}"})
    except Exception as e:
        print(f"  [ERROR] {fname}: {e}")
        failed.append({"file_name": fname, "file_id": fid, "error": str(e)})

# ---- Step 3: Build full inventory of ALL real EDR files ----
print("\n[3] Building full inventory of all real EDR files...")

# Get all 7887036 series from BigQuery too
query2 = """
SELECT DISTINCT file_name, file_id, size_bytes, web_view_link, created_time, owner_names
FROM `project-743aab84-f9a5-4ec7-954.national_audits_legacy.drive_file_index`
WHERE REGEXP_CONTAINS(file_name, r'^7887036|^788703618|^788703620|^78870367|^78870369|^074-0125')
  AND mime_type != 'application/vnd.google-apps.folder'
ORDER BY file_name
"""
df_7887036 = index_client.query(query2).to_dataframe()
print(f"  Found {len(df_7887036)} files in 7887036 series")

# Combine both series
import pandas as pd
df_all = pd.concat([df_7887036, df_7969270], ignore_index=True).drop_duplicates(subset=["file_id"])

# Add local file inventory from Private_EDR_2025_Real
local_files = []
for fname in os.listdir(DEST_DIR):
    fpath = os.path.join(DEST_DIR, fname)
    local_files.append({
        "local_file_name": fname,
        "local_size_bytes": os.path.getsize(fpath),
        "local_path": fpath
    })

print(f"\n  Total unique drive files: {len(df_all)}")
print(f"  Total local staged files: {len(local_files)}")

# ---- Step 4: Ingest inventory into BigQuery ----
print(f"\n[4] Ingesting inventory to BigQuery: {BQ_PROJECT}.{BQ_DATASET}.{BQ_TABLE}...")
bq_client = bigquery.Client(project=BQ_PROJECT)

# Ensure dataset exists
try:
    bq_client.get_dataset(BQ_DATASET)
except Exception:
    bq_client.create_dataset(bigquery.Dataset(f"{BQ_PROJECT}.{BQ_DATASET}"))
    print(f"  Created dataset: {BQ_DATASET}")

# Build rows
rows = []
for _, row in df_all.iterrows():
    rows.append({
        "file_name": str(row.get("file_name", "")),
        "file_id": str(row.get("file_id", "")),
        "size_bytes": int(row.get("size_bytes", 0)) if pd.notna(row.get("size_bytes")) else 0,
        "web_view_link": str(row.get("web_view_link", "")),
        "created_time": str(row.get("created_time", "")),
        "owner_names": str(row.get("owner_names", "")),
        "edr_order_series": "7887036" if str(row.get("file_name","")).startswith(("7887036","78870","074-0125")) else "7969270",
        "source": "google_drive_index",
        "staged_locally": any(f["local_file_name"] == str(row.get("file_name","")) for f in local_files)
    })

# Add locally staged files not in drive index
drive_names = set(r["file_name"] for r in rows)
for lf in local_files:
    if lf["local_file_name"] not in drive_names:
        rows.append({
            "file_name": lf["local_file_name"],
            "file_id": "",
            "size_bytes": lf["local_size_bytes"],
            "web_view_link": "",
            "created_time": "",
            "owner_names": "local_only",
            "edr_order_series": "7887036" if lf["local_file_name"].startswith(("7887036","78870","074-0125","Volume-III")) else "7969270",
            "source": "local_staged",
            "staged_locally": True
        })

schema = [
    bigquery.SchemaField("file_name", "STRING"),
    bigquery.SchemaField("file_id", "STRING"),
    bigquery.SchemaField("size_bytes", "INTEGER"),
    bigquery.SchemaField("web_view_link", "STRING"),
    bigquery.SchemaField("created_time", "STRING"),
    bigquery.SchemaField("owner_names", "STRING"),
    bigquery.SchemaField("edr_order_series", "STRING"),
    bigquery.SchemaField("source", "STRING"),
    bigquery.SchemaField("staged_locally", "BOOL"),
]

table_ref = f"{BQ_PROJECT}.{BQ_DATASET}.{BQ_TABLE}"
job_config = bigquery.LoadJobConfig(
    schema=schema,
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
)

job = bq_client.load_table_from_json(rows, table_ref, job_config=job_config)
job.result()

print(f"\n[SUCCESS] Ingested {len(rows)} records into {table_ref}")
print(f"\n  Downloaded: {len([d for d in downloaded if d['status']=='downloaded'])}")
print(f"  Already existed: {len([d for d in downloaded if d['status']=='already_exists'])}")
print(f"  Failed: {len(failed)}")
if failed:
    print("  Failed files:")
    for f in failed:
        print(f"    - {f['file_name']}: {f['error']}")
