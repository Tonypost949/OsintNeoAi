from google.cloud import bigquery

client = bigquery.Client(project='noble-beanbag-497411-m4')
project = client.project
print(f"Project from client: {project}")
print(f"Client location: {client.location}")
print()

datasets = list(client.list_datasets())
print(f"Number of datasets found: {len(datasets)}\n")

for dataset in datasets:
    dataset_ref = client.dataset(dataset.dataset_id)
    print(f"Dataset: {dataset.dataset_id}")
    try:
        tables = list(client.list_tables(dataset_ref))
        if tables:
            for table in tables:
                print(f"  - {table.table_id}")
        else:
            print("  (no tables)")
    except Exception as e:
        print(f"  Error listing tables: {e}")
    print()
