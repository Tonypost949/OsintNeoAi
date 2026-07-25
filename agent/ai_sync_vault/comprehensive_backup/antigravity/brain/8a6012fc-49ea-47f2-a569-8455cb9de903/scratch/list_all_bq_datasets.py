from google.cloud import bigquery

projects = ["project-743aab84-f9a5-4ec7-954", "project-9c94c2fa-3af4-49f1-a7b"]

for project_id in projects:
    print(f"\n================ Datasets in {project_id} ================")
    client = bigquery.Client(project=project_id)
    try:
        datasets = list(client.list_datasets())
        if datasets:
            for dataset in datasets:
                print(f"- Dataset ID: {dataset.dataset_id}")
                tables = list(client.list_tables(dataset.dataset_id))
                for table in tables:
                    print(f"  |-- Table: {table.table_id} (Type: {table.table_type})")
        else:
            print("[ ] No datasets found.")
    except Exception as e:
        print(f"[ERROR] Failed to list datasets for {project_id}: {e}")
