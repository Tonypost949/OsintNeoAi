from google.cloud import bigquery

bq = bigquery.Client(project="noble-beanbag-497411-m4")
P = "noble-beanbag-497411-m4"

print("=== CHECKING STATE TABLES IN UNCLAIMED_PROPERTY ===")
for state in ["texas", "new_york"]:
    table_id = f"{P}.unclaimed_property.{state}_unclaimed_raw"
    try:
        table = bq.get_table(table_id)
        print(f"Table: {state}_unclaimed_raw | Rows: {table.num_rows} | Schema verified.")
    except Exception as e:
        print(f"Table: {state}_unclaimed_raw | Status: Not loaded yet or error: {e}")
