from google.cloud import bigquery

client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

def main():
    table_ref = client.dataset("ppp_rico").table("hb_llcs")
    table = client.get_table(table_ref)
    print(f"Table: {table.project}.{table.dataset_id}.{table.table_id}")
    cols = [f"{f.name} ({f.field_type})" for f in table.schema]
    print(f"Columns: {', '.join(cols)}")

if __name__ == "__main__":
    main()
