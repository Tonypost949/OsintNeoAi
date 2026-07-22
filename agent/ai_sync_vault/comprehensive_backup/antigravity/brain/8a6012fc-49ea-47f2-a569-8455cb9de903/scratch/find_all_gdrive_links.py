from google.cloud import bigquery

client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

filenames = [
    "Van Buren",
    "Sanborn Map Legend",
    "Appendix-D",
    "Preliminary Sanborn",
    "sanborn.pdf"
]

print("[*] Searching Google Drive Index in BigQuery for EDR 2025 files...")
for name in filenames:
    query = f"""
    SELECT file_name, file_id, web_view_link, size_bytes
    FROM `project-743aab84-f9a5-4ec7-954.national_audits_legacy.drive_file_index`
    WHERE LOWER(file_name) LIKE '%{name.lower()}%'
    """
    try:
        df = client.query(query).to_dataframe()
        if df.empty:
            print(f"[ ] '{name}' — NOT found in BigQuery index")
        else:
            print(f"[+] '{name}' — FOUND:")
            print(df.to_string(index=False))
            print("-" * 50)
    except Exception as e:
        print(f"[ERROR] Failed to query '{name}': {e}")
