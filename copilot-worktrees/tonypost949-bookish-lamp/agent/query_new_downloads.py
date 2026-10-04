from google.cloud import bigquery

GCP_PROJECT = "noble-beanbag-497411-m4"
client = bigquery.Client(project=GCP_PROJECT)

# Query to list files uploaded to the sharedall folder
query = """
SELECT file_name, mime_type, size_bytes, web_view_link, scan_timestamp
FROM `noble-beanbag-497411-m4.national_audits.drive_file_index`
WHERE '1q5bmZJQ9IuSudsie1KNuMWZ0mbfu6-gE' IN UNNEST(parent_folder_ids)
ORDER BY scan_timestamp DESC
LIMIT 15
"""

print("Running BigQuery verification query for new uploads...")
query_job = client.query(query)
results = query_job.result()

print("\n--- NEWLY UPLOADED AND INDEXED FILES IN BIGQUERY ---")
for row in results:
    size_kb = (row.size_bytes / 1024) if row.size_bytes else 0
    print(f"File: {row.file_name}")
    print(f"  Mime-Type: {row.mime_type}")
    print(f"  Size: {size_kb:.2f} KB")
    print(f"  Link: {row.web_view_link}")
    print(f"  Indexed At: {row.scan_timestamp}")
    print("-" * 50)
