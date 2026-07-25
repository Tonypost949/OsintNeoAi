from google.cloud import bigquery

client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

# Targeted search query for the specific EDR 2025-2026 reports
query = """
SELECT DISTINCT file_name, created_time, size_bytes, owner_names
FROM `project-743aab84-f9a5-4ec7-954.national_audits_legacy.drive_file_index`
WHERE (
    LOWER(file_name) LIKE '%edr%' 
    OR LOWER(file_name) LIKE '%assessment%' 
    OR LOWER(file_name) LIKE '%sanborn%'
    OR LOWER(file_name) LIKE '%appendix-d%'
  )
  AND (
    EXTRACT(YEAR FROM created_time) IN (2025, 2026)
    OR EXTRACT(YEAR FROM modified_time) IN (2025, 2026)
  )
ORDER BY created_time DESC
LIMIT 40
"""

print("[*] Running targeted 2025-2026 EDR/ESA report scan in BigQuery...")
try:
    df = client.query(query).to_dataframe()
    if df.empty:
        print("[!] No records found.")
    else:
        print(f"[+] Found {len(df)} matching reports:")
        print(df.to_string(index=False))
except Exception as e:
    print(f"[ERROR] Query failed: {e}")
