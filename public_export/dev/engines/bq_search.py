from google.cloud import bigquery
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\OsintNeoAi\\gcp_adc.json"
client = bigquery.Client(project="noble-beanbag-497411-m4")
query = """
SELECT file_name, web_view_link 
FROM `noble-beanbag-497411-m4.national_audits.drive_file_index` 
WHERE LOWER(file_name) LIKE '%password%' 
   OR LOWER(file_name) LIKE '%login%' 
   OR LOWER(file_name) LIKE '%designplusmarketing%'
LIMIT 50
"""
rows = client.query(query).result()
for r in rows:
    print(f"{r.file_name}: {r.web_view_link}")
