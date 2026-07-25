import os
from google.cloud import bigquery

folder_path = r"C:\Users\HP\OneDrive\Documents\opencode_work\Private_EDR_2025_Real"
project_id = "project-9c94c2fa-3af4-49f1-a7b"
table_id = f"{project_id}.forensic_layers.real_edr_inventory"

client = bigquery.Client(project=project_id)

rows_to_insert = []
for f in os.listdir(folder_path):
    file_path = os.path.join(folder_path, f)
    if os.path.isfile(file_path):
        size = os.path.getsize(file_path)
        
        # Determine order ID from filename
        order_series = "unknown"
        if "7887036" in f:
            order_series = "7887036"
        elif "7969270" in f:
            order_series = "7969270"
            
        row = {
            "file_name": f,
            "file_id": "", # Staged locally, no drive file ID
            "size_bytes": size,
            "web_view_link": "",
            "created_time": "",
            "owner_names": "Anthony",
            "edr_order_series": order_series,
            "source": "Local Staged",
            "staged_locally": True
        }
        rows_to_insert.append(row)

if rows_to_insert:
    print(f"Prepared {len(rows_to_insert)} rows to insert into {table_id}...")
    
    # Overwrite the table content using WRITE_TRUNCATE
    job_config = bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField("file_name", "STRING"),
            bigquery.SchemaField("file_id", "STRING"),
            bigquery.SchemaField("size_bytes", "INTEGER"),
            bigquery.SchemaField("web_view_link", "STRING"),
            bigquery.SchemaField("created_time", "STRING"),
            bigquery.SchemaField("owner_names", "STRING"),
            bigquery.SchemaField("edr_order_series", "STRING"),
            bigquery.SchemaField("source", "STRING"),
            bigquery.SchemaField("staged_locally", "BOOLEAN"),
        ],
        write_disposition="WRITE_TRUNCATE",
    )
    
    try:
        load_job = client.load_table_from_json(
            rows_to_insert,
            table_id,
            job_config=job_config
        )
        load_job.result()  # Wait for the job to complete.
        print(f"Successfully loaded inventory into {table_id}!")
    except Exception as e:
        print(f"Error during load job: {e}")
else:
    print("No files found to insert.")
