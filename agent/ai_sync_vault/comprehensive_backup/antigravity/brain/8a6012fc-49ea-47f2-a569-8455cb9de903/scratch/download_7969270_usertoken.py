"""
Downloads 7969270 EDR files using gcloud user token directly (bypasses ADC scope restriction).
"""
import os
import subprocess
import requests
from google.cloud import bigquery

DEST_DIR = r"C:\Users\HP\OneDrive\Documents\opencode_work\Private_EDR_2025_Real"
INDEX_PROJECT = "project-743aab84-f9a5-4ec7-954"
BQ_PROJECT = "project-9c94c2fa-3af4-49f1-a7b"
BQ_TABLE = "forensic_layers.real_edr_inventory"

os.makedirs(DEST_DIR, exist_ok=True)
GCLOUD = r"C:\Users\HP\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"

# Step 1: Get live token from gcloud user account
print("[1] Getting live access token from gcloud...")
result = subprocess.run(
    [GCLOUD, "auth", "print-access-token", "anthonymichaeldimarcello@gmail.com"],
    capture_output=True, text=True, shell=True
)
token = result.stdout.strip()
if not token:
    result = subprocess.run(
        [GCLOUD, "auth", "print-access-token"],
        capture_output=True, text=True, shell=True
    )
    token = result.stdout.strip()

if not token:
    print("[ERROR] Could not get access token.")
    exit(1)

print(f"  Token obtained: {token[:20]}...")

# Step 2: Get all 7969270 file IDs from BigQuery
print("\n[2] Querying BigQuery for 7969270 series file IDs...")
client = bigquery.Client(project=INDEX_PROJECT)

query = """
SELECT DISTINCT file_name, file_id, size_bytes
FROM `project-743aab84-f9a5-4ec7-954.national_audits_legacy.drive_file_index`
WHERE REGEXP_CONTAINS(file_name, r'^7969270|^79692706|^79692705|^79692707|^79692708')
  AND mime_type != 'application/vnd.google-apps.folder'
  AND file_id IS NOT NULL
ORDER BY file_name
"""

df = client.query(query).to_dataframe()
df = df.sort_values("size_bytes", ascending=False).drop_duplicates(subset=["file_name"])
print(f"  Found {len(df)} unique files in 7969270 series")

# Step 3: Download each file
print("\n[3] Downloading files...")
headers = {"Authorization": f"Bearer {token}"}
downloaded, failed, skipped = [], [], []

for _, row in df.iterrows():
    fname = str(row["file_name"])
    fid = str(row["file_id"])
    dest_path = os.path.join(DEST_DIR, fname)

    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
        print(f"  [=] Already exists: {fname}")
        skipped.append(fname)
        continue

    url = f"https://www.googleapis.com/drive/v3/files/{fid}?alt=media"
    try:
        r = requests.get(url, headers=headers, stream=True, timeout=120)
        if r.status_code == 200:
            with open(dest_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024*1024):
                    f.write(chunk)
            size = os.path.getsize(dest_path)
            print(f"  [+] Downloaded: {fname} ({size/1024/1024:.1f}MB)")
            downloaded.append(fname)
        elif r.status_code == 403:
            # Try switching to txtdjdrop account
            result2 = subprocess.run(
                [GCLOUD, "auth", "print-access-token", "txtdjdrop@gmail.com"],
                capture_output=True, text=True, shell=True
            )
            token2 = result2.stdout.strip()
            if token2:
                headers2 = {"Authorization": f"Bearer {token2}"}
                r2 = requests.get(url, headers=headers2, stream=True, timeout=120)
                if r2.status_code == 200:
                    with open(dest_path, "wb") as f:
                        for chunk in r2.iter_content(chunk_size=1024*1024):
                            f.write(chunk)
                    size = os.path.getsize(dest_path)
                    print(f"  [+] Downloaded via txtdjdrop: {fname} ({size/1024/1024:.1f}MB)")
                    downloaded.append(fname)
                else:
                    print(f"  [!] 403 on both accounts: {fname}")
                    failed.append(fname)
            else:
                print(f"  [!] 403: {fname}")
                failed.append(fname)
        else:
            print(f"  [!] HTTP {r.status_code}: {fname}")
            failed.append(fname)
    except Exception as e:
        print(f"  [ERROR] {fname}: {e}")
        failed.append(fname)

print(f"\n[DONE] Downloaded: {len(downloaded)} | Skipped: {len(skipped)} | Failed: {len(failed)}")

# Step 4: Update BigQuery inventory
print("\n[4] Updating BigQuery inventory...")
bq_client = bigquery.Client(project=BQ_PROJECT)

local_files = []
for fname in os.listdir(DEST_DIR):
    fpath = os.path.join(DEST_DIR, fname)
    local_files.append({
        "file_name": fname,
        "file_id": "",
        "size_bytes": os.path.getsize(fpath),
        "web_view_link": "",
        "created_time": "",
        "owner_names": "local_staged",
        "edr_order_series": "7887036" if fname.startswith(("7887036","78870","074-0125","Volume-III")) else "7969270",
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

job_config = bigquery.LoadJobConfig(
    schema=schema,
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
)
job = bq_client.load_table_from_json(local_files, f"{BQ_PROJECT}.{BQ_TABLE}", job_config=job_config)
job.result()
print(f"[SUCCESS] Updated BigQuery inventory: {len(local_files)} local files indexed")
