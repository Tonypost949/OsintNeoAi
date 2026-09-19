from google.cloud import bigquery
from google.api_core.exceptions import Conflict

PROJECT_ID = "noble-beanbag-497411-m4"
DATASET_ID = "forensic_layers"
TABLE_ID = "genesis_ledger"

def create_table():
    client = bigquery.Client(project=PROJECT_ID)
    dataset_ref = client.dataset(DATASET_ID)
    
    # Create dataset if it doesn't exist
    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = "US"
    try:
        client.create_dataset(dataset, timeout=30)
        print(f"Created dataset {DATASET_ID}")
    except Conflict:
        pass # Already exists

    table_id = dataset_ref.table(TABLE_ID)
    
    schema = [
        bigquery.SchemaField("receipt_hash", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("parent_hash", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("timestamp_unix", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("source_origin", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("genesis_type", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("target_entity", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("raw_payload", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("ledger_value", "NUMERIC", mode="REQUIRED"),
        bigquery.SchemaField("verification_status", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("enrichment_status", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("metadata", "JSON", mode="NULLABLE"),
    ]
    
    table = bigquery.Table(table_id, schema=schema)
    
    # Time-partition by day, cluster by hash and entity for fast UI queries
    table.time_partitioning = bigquery.TimePartitioning(type_=bigquery.TimePartitioningType.DAY, field="timestamp")
    table.clustering_fields = ["receipt_hash", "target_entity"]
    
    try:
        client.create_table(table, timeout=30)
        print(f"[+] Table {table_id} created and clustered securely.")
    except Conflict:
        print(f"[*] Table {table_id} already exists.")

if __name__ == "__main__":
    create_table()
