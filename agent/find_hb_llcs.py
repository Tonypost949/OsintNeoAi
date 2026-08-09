from google.cloud import bigquery

client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

def main():
    print("Scanning datasets in project project-743aab84-f9a5-4ec7-954...")
    datasets = list(client.list_datasets())
    for dataset in datasets:
        ds_id = dataset.dataset_id
        tables = list(client.list_tables(ds_id))
        for table in tables:
            if "hb_llcs" in table.table_id:
                print(f"FOUND: Dataset '{ds_id}' contains table '{table.table_id}'")
                return
    print("Table 'hb_llcs' not found in any dataset.")

if __name__ == "__main__":
    main()
