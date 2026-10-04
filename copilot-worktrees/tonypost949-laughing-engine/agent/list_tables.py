
from google.cloud import bigquery

def list_dataset_tables():
    """Lists all tables in a given BigQuery dataset."""
    try:
        client = bigquery.Client(project='noble-beanbag-497411-m4')
        dataset_id = "noble-beanbag-497411-m4.ppp_rico"

        print(f"Listing tables in dataset: {dataset_id}")
        print("-" * 50)
        
        tables = client.list_tables(dataset_id)
        
        if tables:
            for table in tables:
                print(table.table_id)
        else:
            print("No tables found in this dataset.")
            
        print("-" * 50)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    list_dataset_tables()
