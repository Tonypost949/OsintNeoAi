from google.cloud import bigquery

client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

query = """
SELECT file_name, mime_type, size_bytes, created_time, owner_emails, web_view_link
FROM `project-743aab84-f9a5-4ec7-954.national_audits_legacy.drive_file_index`
WHERE LOWER(file_name) LIKE '%edr%' 
   OR LOWER(file_name) LIKE '%environmental%' 
   OR LOWER(file_name) LIKE '%phase%'
   OR LOWER(file_name) LIKE '%cameron%'
   OR LOWER(file_name) LIKE '%beach%'
   OR LOWER(file_name) LIKE '%yamada%'
   OR LOWER(file_name) LIKE '%knabb%'
ORDER BY created_time DESC
LIMIT 100
"""

print("[*] Querying national_audits_legacy.drive_file_index with correct schema...")
try:
    df = client.query(query).to_dataframe()
    if df.empty:
        print("[!] No matching files found in drive_file_index.")
    else:
        print(f"[+] Found {len(df)} matching files in Google Drive index:")
        print(df.to_string(index=False))
except Exception as e:
    print(f"[ERROR] Query failed: {e}")
