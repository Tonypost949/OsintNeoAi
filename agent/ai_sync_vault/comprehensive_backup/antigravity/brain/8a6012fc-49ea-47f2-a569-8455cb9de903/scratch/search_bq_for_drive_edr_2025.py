from google.cloud import bigquery

client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

query = """
SELECT file_name, mime_type, size_bytes, created_time, owner_names, web_view_link
FROM `project-743aab84-f9a5-4ec7-954.national_audits_legacy.drive_file_index`
WHERE LOWER(file_name) LIKE '%edr%' 
   OR LOWER(file_name) LIKE '%lightbox%'
   OR LOWER(file_name) LIKE '%sanborn%'
   OR LOWER(file_name) LIKE '%van buren%'
ORDER BY created_time DESC
"""

print("[*] Querying BigQuery drive_file_index for EDR 2025 files...")
try:
    df = client.query(query).to_dataframe()
    if df.empty:
        print("[!] No records found in the index.")
    else:
        print(f"[+] Found {len(df)} matching records:")
        print(df.to_string(index=False))
except Exception as e:
    print(f"[ERROR] Query failed: {e}")
