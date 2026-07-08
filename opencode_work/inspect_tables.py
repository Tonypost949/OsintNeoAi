from google.cloud import bigquery
client = bigquery.Client(project='noble-beanbag-497411-m4')

for dataset_id, table_id in [
    ('ai_sandbox', 'findings'),
    ('ai_sandbox', 'hb_surface_flow'),
    ('hb_church_osint', 'entities'),
    ('hb_church_osint', 'properties'),
    ('hb_church_osint', 'relationships'),
]:
    print(f"\n=== {dataset_id}.{table_id} ===")
    try:
        table = client.get_table(f"{dataset_id}.{table_id}")
        print(f"Rows: {table.num_rows}, Size: {table.num_bytes}")
        for f in table.schema[:20]:
            print(f"  {f.name}: {f.field_type}")
        if len(table.schema) > 20:
            print(f"  ...and {len(table.schema)-20} more fields")
    except Exception as e:
        print(f"Error: {e}")
