from google.cloud import bigquery

GCP_PROJECT = "project-743aab84-f9a5-4ec7-954"

def list_all():
    client = bigquery.Client(project=GCP_PROJECT)
    datasets = list(client.list_datasets())
    
    for ds in datasets:
        ds_id = ds.dataset_id
        print(f"\n================ DATASET: {ds_id} ================")
        try:
            tables = list(client.list_tables(ds_id))
            if not tables:
                print("  (No tables)")
                continue
            for t in tables:
                table_ref = f"{GCP_PROJECT}.{ds_id}.{t.table_id}"
                try:
                    count_query = f"SELECT COUNT(*) as count FROM `{table_ref}`"
                    job = client.query(count_query)
                    count = list(job.result())[0].count
                    print(f"  - Table: {t.table_id} | Rows: {count}")
                except Exception as ex:
                    print(f"  - Table: {t.table_id} | Error getting count: {ex}")
        except Exception as e:
            print(f"Error listing tables for dataset {ds_id}: {e}")

if __name__ == "__main__":
    list_all()
