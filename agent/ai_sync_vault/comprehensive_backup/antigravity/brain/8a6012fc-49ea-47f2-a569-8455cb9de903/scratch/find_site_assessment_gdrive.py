from google.cloud import bigquery

client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

query = """
SELECT file_name, file_id, web_view_link, size_bytes
FROM `project-743aab84-f9a5-4ec7-954.national_audits_legacy.drive_file_index`
WHERE LOWER(file_name) LIKE '%site assessment report%' AND size_bytes > 50000000
"""

try:
    df = client.query(query).to_dataframe()
    if df.empty:
        print("[!] Not found in index.")
    else:
        print("[+] Found Site Assessment Report in Google Drive Index:")
        print(df.to_string(index=False))
except Exception as e:
    print(f"[ERROR] Query failed: {e}")
