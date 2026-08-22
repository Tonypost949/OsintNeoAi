from google.cloud import bigquery

client = bigquery.Client(project='noble-beanbag-497411-m4')

print("=== LISTING BIGQUERY DATASETS AND TABLES ===")
for dataset in client.list_datasets():
    print(f"Dataset: {dataset.dataset_id}")
    dataset_ref = client.dataset(dataset.dataset_id)
    for table in client.list_tables(dataset_ref):
        print(f"  Table: {table.table_id}")
