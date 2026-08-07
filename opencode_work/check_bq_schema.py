from google.cloud import bigquery
c = bigquery.Client(project="noble-beanbag-497411-m4")
q = """
SELECT column_name, data_type
FROM `noble-beanbag-497411-m4.national_audits.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = "drive_file_index"
ORDER BY ordinal_position
"""
df = c.query(q).to_dataframe()
print("drive_file_index schema:")
print(df.to_string())
