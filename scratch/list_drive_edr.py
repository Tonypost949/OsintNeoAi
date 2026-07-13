from google.cloud import bigquery
import os
import json

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\HP\AppData\Roaming\gcloud\legacy_credentials\txtdjdrop@gmail.com\adc.json"
client = bigquery.Client(project="noble-beanbag-497411-m4")

q = """
SELECT file_name, web_view_link, created_time
FROM `noble-beanbag-497411-m4.national_audits.drive_file_index`
WHERE LOWER(file_name) LIKE '%edr%' 
   OR LOWER(file_name) LIKE '%radius%'
   OR LOWER(file_name) LIKE '%geocheck%'
ORDER BY created_time DESC
LIMIT 100
"""

results = [dict(r) for r in client.query(q).result()]
print(f"Found {len(results)} files in Drive index matching EDR/Radius patterns.")
for r in results[:20]:
    print(f" - {r['file_name']} (Created: {r['created_time']})")
