import os
from pathlib import Path
from google.cloud import bigquery
from google.cloud import storage
import subprocess

PROJECT = "noble-beanbag-497411-m4"
WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")
BUCKET = "osint-ai-evidence-vault-m4"
GCS_PREFIX = "bq_exports"

client = bigquery.Client(project=PROJECT)
storage_client = storage.Client(project=PROJECT)

bucket = storage_client.bucket(BUCKET)
if not bucket.exists():
    print(f"Bucket {BUCKET} does not exist!")
    print("Creating it...")
    bucket = storage_client.create_bucket(BUCKET, location="US")
    print(f"Created bucket: {bucket.name}")
else:
    print(f"Using existing bucket: {BUCKET}")

table_ref = f"{PROJECT}.ppp_rico.ppp_up_to_150k"
csv_local = WORK_DIR / "ppp_rico_ppp_up_to_150k.csv"
gcs_uri = f"gs://{BUCKET}/{GCS_PREFIX}/ppp_up_to_150k/*.csv"

print(f"\nStarting BigQuery export to GCS: {gcs_uri}")
from google.cloud import bigquery
job_config = bigquery.ExtractJobConfig()
job_config.destination_format = "CSV"
job = client.extract_table(
    table_ref,
    gcs_uri,
    location="US",
    job_config=job_config
)
print("Waiting for export job...", end="", flush=True)
job.result()
print(" DONE")

print("\nDownloading from GCS...")
blobs = sorted(list(bucket.list_blobs(prefix=f"{GCS_PREFIX}/ppp_up_to_150k")), key=lambda b: b.name)
print(f"Found {len(blobs)} shard files")

for i, blob in enumerate(blobs):
    shard_path = WORK_DIR / f"ppp_up_to_150k_part{i:03d}.csv"
    print(f"  Downloading {blob.name}...", end="", flush=True)
    blob.download_to_filename(str(shard_path))
    print(f" DONE ({blob.size / 1024 / 1024:.1f} MB)")

print("\nMerging shards...")
first = True
total_rows = 0
with open(csv_local, 'wb') as out:
    for i, blob in enumerate(blobs):
        shard_path = WORK_DIR / f"ppp_up_to_150k_part{i:03d}.csv"
        with open(shard_path, 'rb') as inp:
            data = inp.read()
        if first:
            out.write(data)
            first = False
        else:
            lines = data.split(b'\n')
            out.write(b'\n'.join(lines[1:]))
        total_rows += sum(1 for line in open(shard_path, 'rb')) - 1
        os.remove(shard_path)
        print(f"  Merged shard {i+1}/{len(blobs)}")

print(f"\nDONE! {total_rows} total rows -> {csv_local.name}")

print("\nCleaning up GCS shards...")
for blob in blobs:
    blob.delete()
print("Clean.")
