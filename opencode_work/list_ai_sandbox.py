from google.cloud import bigquery
client = bigquery.Client(project='noble-beanbag-497411-m4')

print("Datasets:")
for ds in client.list_datasets():
    print(f"  {ds.dataset_id}")

print("\nai_sandbox tables:")
try:
    tables = client.list_tables('ai_sandbox')
    for t in tables:
        print(f"  {t.table_id} ({t.table_type})")
except Exception as e:
    print(f"Error: {e}")
