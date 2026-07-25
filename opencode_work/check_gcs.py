from google.cloud import storage
client = storage.Client(project="noble-beanbag-497411-m4")
bucket = client.bucket("osint-ai-evidence-vault-m4")
blobs = list(bucket.list_blobs(prefix="bq_exports/ppp_up_to_150k"))
print(f"GCS shards found: {len(blobs)}")
for b in blobs:
    print(f"  {b.name} - {b.size/1024/1024:.1f} MB")
