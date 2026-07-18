from google.cloud import bigquery

client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

query = """
SELECT DISTINCT file_name, file_id, created_time, size_bytes, owner_names, web_view_link
FROM `project-743aab84-f9a5-4ec7-954.national_audits_legacy.drive_file_index`
WHERE REGEXP_CONTAINS(file_name, r'^7887036')
ORDER BY file_name
"""

print("[*] Querying BigQuery for 7887036 series real EDR files...")
try:
    df = client.query(query).to_dataframe()
    if df.empty:
        print("[!] Not found in drive_file_index — checking other datasets...")
        # Check all tables across the dataset
        q2 = """
        SELECT DISTINCT table_id
        FROM `project-743aab84-f9a5-4ec7-954.national_audits_legacy.INFORMATION_SCHEMA.TABLES`
        """
        tables = client.query(q2).to_dataframe()
        print("Tables in national_audits_legacy:")
        print(tables.to_string(index=False))
    else:
        print(f"[+] Found {len(df)} entries for 7887036 series in BigQuery:")
        import pandas as pd
        pd.set_option('display.max_colwidth', None)
        print(df.to_string(index=False))
except Exception as e:
    print(f"[ERROR]: {e}")
