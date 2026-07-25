from google.cloud import bigquery

client = bigquery.Client()
dataset_id = "ppp_rico"

tables = list(client.list_tables(f"{client.project}.{dataset_id}"))
print(f"Tables in {dataset_id}:")
for table in tables:
    print(f"  - {table.table_id}")
    t = client.get_table(table.reference)
    print("    Columns:")
    for field in t.schema:
        print(f"      * {field.name}: {field.field_type}")
