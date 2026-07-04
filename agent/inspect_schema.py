
from google.cloud import bigquery
from google.api_core.exceptions import NotFound

def inspect_table_schema():
    """Connects to BigQuery and prints the schema of the specified table."""
    try:
        client = bigquery.Client(project='project-743aab84-f9a5-4ec7-954')
        table_id = "project-743aab84-f9a5-4ec7-954.ppp_rico.ppp_150k_plus"

        print(f"Inspecting schema for table: {table_id}")
        table = client.get_table(table_id)  # API request

        print("\\n" + "="*50)
        print("TABLE SCHEMA")
        print("="*50)
        for field in table.schema:
            print(f"Name: {field.name:<30} Type: {field.field_type:<10} Mode: {field.mode}")
            if field.description:
                print(f"  Description: {field.description}")
        print("="*50 + "\\n")

    except NotFound:
        print(f"Error: Table {table_id} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    inspect_table_schema()
