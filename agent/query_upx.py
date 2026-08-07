from google.cloud import bigquery

client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

query = """
SELECT file_id, file_name, mime_type, web_view_link
FROM `project-743aab84-f9a5-4ec7-954.national_audits.drive_file_index`
WHERE file_name LIKE '%UPX1978058%' OR file_name LIKE '%Chen_Yamada%'
"""

try:
    results = client.query(query).result()
    count = 0
    for row in results:
        count += 1
        print(f"File: {row.file_name} | ID: {row.file_id} | Link: {row.web_view_link}")
    print(f"Found {count} files matching UPX1978058 / Chen_Yamada")
except Exception as e:
    print(f"Error querying BigQuery: {e}")
