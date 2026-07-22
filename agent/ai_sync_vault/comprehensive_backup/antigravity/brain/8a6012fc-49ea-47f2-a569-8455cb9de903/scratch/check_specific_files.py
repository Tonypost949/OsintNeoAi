from google.cloud import bigquery

client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

filenames = [
    "Appendix-D---EDR-Report.pdf",
    "srf_edr_logo_v2",
    "edr-lightbox-c8b3becb.min",
    "ERA EDR",
    "EDR Lightbox_files"
]

print("[*] Checking if specific EDR 2025 files exist in BigQuery drive_file_index...")
for name in filenames:
    query = f"""
    SELECT file_name, mime_type, created_time, web_view_link
    FROM `project-743aab84-f9a5-4ec7-954.national_audits_legacy.drive_file_index`
    WHERE LOWER(file_name) LIKE '%{name.lower()}%'
    """
    try:
        df = client.query(query).to_dataframe()
        if df.empty:
            print(f"[ ] '{name}' — NOT found in index")
        else:
            print(f"[+] '{name}' — FOUND:")
            print(df.to_string(index=False))
    except Exception as e:
        print(f"[ERROR] Failed to query '{name}': {e}")
