from google.cloud import bigquery
bq = bigquery.Client(project='noble-beanbag-497411-m4')

query = """
SELECT file_name, mime_type, modified_time, web_view_link
FROM `noble-beanbag-497411-m4.national_audits.drive_file_index`
WHERE LOWER(file_name) LIKE '%permit%' OR LOWER(file_name) LIKE '%storm%'
ORDER BY modified_time DESC
LIMIT 50
"""
results = bq.query(query).result()
for row in results:
    print(f'{row.file_name} | {row.mime_type} | {row.modified_time} | {row.web_view_link}')