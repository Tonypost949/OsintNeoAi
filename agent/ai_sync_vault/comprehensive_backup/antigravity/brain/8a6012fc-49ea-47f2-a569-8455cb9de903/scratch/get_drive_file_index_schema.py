from google.cloud import bigquery

client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")
table_ref = client.dataset("national_audits_legacy").table("drive_file_index")

try:
    table = client.get_table(table_ref)
    cols = [f"{f.name} ({f.field_type})" for f in table.schema]
    print("[+] Columns in drive_file_index:")
    print(", ".join(cols))
except Exception as e:
    print(f"[ERROR] Failed to get table schema: {e}")
