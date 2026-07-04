from google.cloud import bigquery

projects = [
    "golden-agency-497410-t8",
    "hardy-order-496117-p3",
    "project-743aab84-f9a5-4ec7-954",
    "project-743aab84-f9a5-4ec7-954",
    "superb-router-q8gvj"
]

def audit_all_projects():
    for project in projects:
        print(f"\n==================================================")
        print(f"PROJECT: {project}")
        print(f"==================================================")
        client = bigquery.Client(project=project)
        try:
            datasets = list(client.list_datasets())
            if not datasets:
                print("  (No datasets)")
                continue
            for ds in datasets:
                ds_id = ds.dataset_id
                print(f"\n  Dataset: {ds_id}")
                try:
                    tables = list(client.list_tables(ds_id))
                    if not tables:
                        print("    (No tables)")
                        continue
                    for t in tables:
                        table_ref = f"{project}.{ds_id}.{t.table_id}"
                        try:
                            count_query = f"SELECT COUNT(*) as count FROM `{table_ref}`"
                            job = client.query(count_query)
                            count = list(job.result())[0].count
                            print(f"    - Table: {t.table_id} | Rows: {count}")
                        except Exception as ex:
                            print(f"    - Table: {t.table_id} | Error: {ex}")
                except Exception as ex_ds:
                    print(f"    Error listing tables: {ex_ds}")
        except Exception as e:
            print(f"  Error listing datasets: {e}")

if __name__ == "__main__":
    audit_all_projects()
