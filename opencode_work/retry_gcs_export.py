import os
import logging
from pathlib import Path
from google.cloud import bigquery
from google.cloud import storage
from google.api_core import exceptions

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

PROJECT = "noble-beanbag-497411-m4"
WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")
BUCKET_NAME = "osint-ai-evidence-vault-m4"
GCS_PREFIX = "bq_exports/ppp_up_to_150k"

client = bigquery.Client(project=PROJECT)
storage_client = storage.Client(project=PROJECT)
bucket = storage_client.bucket(BUCKET_NAME)

csv_path = WORK_DIR / "ppp_rico_ppp_up_to_150k.csv"
table_ref = f"{PROJECT}.ppp_rico.ppp_up_to_150k"

existing = 0
if csv_path.exists():
    with open(csv_path) as f:
        existing = sum(1 for _ in f) - 1

t = client.get_table(table_ref)
total = t.num_rows
print(f"Table has {total} rows, local has {existing}")

gcs_uri = f"gs://{BUCKET_NAME}/{GCS_PREFIX}"

print(f"Starting export to {gcs_uri}...")
try:
    job = client.extract_table(
        table_ref,
        gcs_uri,
        location="US"
    )
    print(f"Export job {job.job_id} started, waiting...")
    job.result()
    print("Export complete!")
except Exception as e:
    print(f"Export failed: {e}")
    raise

print("Checking GCS for shards...")
blobs = sorted(list(bucket.list_blobs(prefix=GCS_PREFIX)), key=lambda b: b.name)
print(f"Found {len(blobs)} shards:")
for b in blobs:
    print(f"  {b.name} - {b.size/1024/1024:.1f}MB")

if not blobs:
    raise RuntimeError("No shards found after export!")

print("\nMerging shards...")
first = True
rows_out = 0
with open(csv_path, 'wb' if first else 'ab') as out:
    for i, blob in enumerate(blobs):
        shard_path = WORK_DIR / f"shard_{i:03d}.csv"
        blob.download_to_filename(str(shard_path))
        with open(shard_path, 'rb') as inp:
            data = inp.read()
        lines = data.split(b'\n')
        if first:
            out.write(data)
            first = False
            rows_out = len(lines) - 1
        else:
            out.write(b'\n'.join(lines[1:]))
            rows_out += len(lines) - 1
        os.remove(shard_path)
        print(f"  Merged shard {i+1}/{len(blobs)} ({rows_out} total rows)")

print(f"\nDONE: {csv_path.name} = {rows_out} rows")

print("\nCleaning GCS...")
for blob in blobs:
    blob.delete()
print("All clean.")
