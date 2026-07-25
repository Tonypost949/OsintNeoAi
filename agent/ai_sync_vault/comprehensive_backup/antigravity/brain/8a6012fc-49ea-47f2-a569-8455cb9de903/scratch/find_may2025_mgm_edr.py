from google.cloud import bigquery
import pandas as pd

client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_rows', None)

# Search for May 2025 EDR pulls AND MGM Grand related files
query = """
SELECT DISTINCT file_name, file_id, created_time, size_bytes, owner_names, web_view_link
FROM `project-743aab84-f9a5-4ec7-954.national_audits_legacy.drive_file_index`
WHERE (
    -- Any 7887036 series files from May 2025
    (REGEXP_CONTAINS(file_name, r'^7887036') AND EXTRACT(MONTH FROM created_time) = 5 AND EXTRACT(YEAR FROM created_time) = 2025)
    OR
    -- MGM Grand related files any time
    LOWER(file_name) LIKE '%mgm%'
    OR LOWER(file_name) LIKE '%grand%'
    OR
    -- Any EDR order files from May 2025
    (REGEXP_CONTAINS(file_name, r'^\d{7,}') AND EXTRACT(MONTH FROM created_time) = 5 AND EXTRACT(YEAR FROM created_time) = 2025)
)
ORDER BY created_time DESC
"""

print("[*] Searching BigQuery for May 2025 EDR pulls and MGM Grand files...")
try:
    df = client.query(query).to_dataframe()
    if df.empty:
        print("[!] No results found.")
    else:
        print(f"[+] Found {len(df)} entries:")
        print(df.to_string(index=False))
except Exception as e:
    print(f"[ERROR]: {e}")
