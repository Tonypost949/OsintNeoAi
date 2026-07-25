from google.cloud import bigquery

client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

query = """
SELECT source_folder, path, size, modified_utc 
FROM `project-743aab84-f9a5-4ec7-954.national_audits.local_scan_file_inventory`
WHERE LOWER(path) LIKE '%edr%' 
   OR LOWER(path) LIKE '%environmental%' 
   OR LOWER(path) LIKE '%phase%'
   OR LOWER(path) LIKE '%t10000%'
ORDER BY modified_utc DESC
LIMIT 50
"""

print("[*] Querying national_audits.local_scan_file_inventory in BigQuery for EDR/Environmental/Phase files...")
try:
    df = client.query(query).to_dataframe()
    if df.empty:
        print("[!] No records matching EDR/Environmental/Phase found in the file inventory table.")
    else:
        print(f"[+] Found {len(df)} matching records:")
        print(df.to_string(index=False))
except Exception as e:
    print(f"[ERROR] Query failed: {e}")
