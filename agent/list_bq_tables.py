from google.cloud import bigquery

client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

datasets = ["ppp_rico", "national_audits", "forensic_layers"]

for ds_name in datasets:
    print(f"--- Tables in dataset: {ds_name} ---")
    try:
        dataset_ref = client.dataset(ds_name)
        tables = client.list_tables(dataset_ref)
        for t in tables:
            print(f"- Table ID: {t.table_id} (Full: {t.project}.{t.dataset_id}.{t.table_id})")
            # print schema briefly
            table_obj = client.get_table(t)
            cols = [f.name for f in table_obj.schema]
            print(f"  Columns: {', '.join(cols)}")
    except Exception as e:
        print(f"Error listing tables for {ds_name}: {e}")
    print("-" * 50)
