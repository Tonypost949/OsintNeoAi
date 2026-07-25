from google.cloud import bigquery
client = bigquery.Client(project='noble-beanbag-497411-m4')
try:
    query = "SELECT schema_name FROM `region-us`.INFORMATION_SCHEMA.SCHEMATA LIMIT 50"
    result = client.query(query).result()
    print("Datasets via INFORMATION_SCHEMA:")
    for row in result:
        print(row.schema_name)
except Exception as e:
    print(f"Error: {e}")
