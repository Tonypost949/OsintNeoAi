import os
import json
from google.cloud import bigquery

bq_client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

print("Querying drive_file_index...")
query = """
SELECT file_id, file_name, mime_type, modified_time, owner_emails, web_view_link
FROM `project-743aab84-f9a5-4ec7-954.national_audits.drive_file_index`
ORDER BY file_name
"""

try:
    results = bq_client.query(query).result()
    files = []
    for r in results:
        files.append({
            "file_id": r.file_id,
            "file_name": r.file_name,
            "mime_type": r.mime_type,
            "modified_time": str(r.modified_time),
            "owner_emails": r.owner_emails,
            "web_view_link": r.web_view_link
        })
    
    output_path = "drive_files_list.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(files, f, indent=2)
    print(f"Saved {len(files)} file records to {output_path}")

except Exception as e:
    print(f"Error querying BigQuery: {e}")
