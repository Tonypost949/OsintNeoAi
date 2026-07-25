from google.cloud import bigquery

client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

query = """
SELECT column_name, data_type 
FROM `project-743aab84-f9a5-4ec7-954.national_audits_legacy.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = 'drive_file_index'
"""

try:
    df = client.query(query).to_dataframe()
    print("Schema:")
    print(df.to_string(index=False))
except Exception as e:
    print(f"Error: {e}")
