import os
import json
import datetime
from google.cloud import bigquery

PROJECT_ID = "project-743aab84-f9a5-4ec7-954"
DATASET_ID = "ai_sandbox_2"
TABLE_ID = "gmail_amd949609_hits"
FILE_PATH = "gmail_amd949609_hits.json"

def main():
    if not os.path.exists(FILE_PATH):
        print(f"Error: Could not find {FILE_PATH}. Please make sure you downloaded it from Google Drive into this folder.")
        return
        
    print(f"Reading {FILE_PATH}...")
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print(f"Found {len(data)} emails matching the search!")
    
    bq_client = bigquery.Client(project=PROJECT_ID)
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    
    schema = [
        bigquery.SchemaField("id", "STRING"),
        bigquery.SchemaField("date", "TIMESTAMP"),
        bigquery.SchemaField("from_user", "STRING"),
        bigquery.SchemaField("subject", "STRING"),
        bigquery.SchemaField("snippet", "STRING"),
        bigquery.SchemaField("query_match", "STRING"),
        bigquery.SchemaField("scanned_at", "TIMESTAMP"),
    ]
    # Ensure dataset exists and has Sandbox limits
    dataset_ref = bq_client.dataset(DATASET_ID)
    try:
        bq_client.get_dataset(dataset_ref)
    except Exception:
        print(f"Creating dataset {DATASET_ID} for Sandbox...")
        dataset = bigquery.Dataset(dataset_ref)
        dataset.default_table_expiration_ms = 59 * 24 * 60 * 60 * 1000  # 59 days
        bq_client.create_dataset(dataset)

    table = bigquery.Table(table_ref, schema=schema)
    try:
        bq_client.get_table(table)
    except Exception:
        print("Table not found. Creating it...")
        bq_client.create_table(table)
    
    # Format rows for BigQuery
    rows_to_insert = []
    for msg in data:
        rows_to_insert.append({
            "id": msg.get("id", ""),
            "date": msg.get("date", ""),
            "from_user": msg.get("from_user", ""),
            "subject": msg.get("subject", ""),
            "snippet": msg.get("snippet", ""),
            "query_match": "in:sent AMD949609",
            "scanned_at": datetime.datetime.utcnow().isoformat()
        })
        
    if not rows_to_insert:
        print("No hits to load.")
        return
        
    # BigQuery Sandbox forbids streaming inserts (insert_rows_json). We must use a Load Job.
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".jsonl", encoding="utf-8") as temp_file:
        for row in rows_to_insert:
            temp_file.write(json.dumps(row) + "\n")
        temp_file_path = temp_file.name

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        schema=schema,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND
    )
    
    print(f"Loading {len(rows_to_insert)} rows into BigQuery ({table_ref}) via Load Job...")
    with open(temp_file_path, "rb") as source_file:
        load_job = bq_client.load_table_from_file(source_file, table_ref, job_config=job_config)
    
    load_job.result()  # Wait for the job to complete
    os.remove(temp_file_path)
    
    print("[+] SUCCESS! All emails have been loaded into BigQuery.")

if __name__ == "__main__":
    main()
