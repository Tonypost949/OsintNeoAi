import json
import os
from google.cloud import bigquery

# Initialize BigQuery client
client = bigquery.Client()
dataset_id = "national_audits"

print("Step 1/3: Loading forensic_master_spreadsheet from GCS...")
# We use GCS path for faster and multi-threaded loading of the CSV
table_ref = client.dataset(dataset_id).table("forensic_master")
job_config = bigquery.LoadJobConfig(
    autodetect=True,
    skip_leading_rows=1,
    source_format=bigquery.SourceFormat.CSV,
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
)

gcs_uri = "gs://osintneoxl/AG2OSINTNEOMAXX/forensic_master_spreadsheet.csv"
try:
    load_job = client.load_table_from_uri(gcs_uri, table_ref, job_config=job_config)
    load_job.result()  # Wait for the job to complete
    print(f"Successfully loaded {load_job.output_rows} rows into {dataset_id}.forensic_master")
except Exception as e:
    print(f"Error loading forensic_master from GCS: {e}")

# Step 2/3: Inspect conversations.json and load it
conversations_path = r"C:\Users\HP\Downloads\deepseek_data-2026-07-02 (1)\conversations.json"
print("\nStep 2/3: Inspecting and loading conversations.json...")
if os.path.exists(conversations_path):
    try:
        with open(conversations_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"Loaded JSON. Type: {type(data)}")
            
            # If it's a list, let's see what keys are in the first item
            if isinstance(data, list):
                print(f"Total conversations found: {len(data)}")
                if len(data) > 0:
                    print(f"Sample item keys: {list(data[0].keys())}")
                    
                # Standardize nested conversation elements into a robust BigQuery schema
                # We can store the raw message payload as a JSON string to ensure no nested array schema mismatches occur
                flat_data = []
                for idx, conv in enumerate(data):
                    flat_conv = {
                        "id": conv.get("id", f"conv_{idx}"),
                        "title": conv.get("title", f"Conversation {idx}"),
                        "create_time": str(conv.get("create_time", conv.get("created_at", ""))),
                        "update_time": str(conv.get("update_time", conv.get("updated_at", ""))),
                        "messages_raw": json.dumps(conv.get("messages", conv.get("chat_log", conv.get("steps", conv))))
                    }
                    flat_data.append(flat_conv)
                
                # Load flat data to BQ
                conv_table_ref = client.dataset(dataset_id).table("deepseek_conversations")
                conv_job_config = bigquery.LoadJobConfig(
                    autodetect=True,
                    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
                )
                conv_job = client.load_table_from_json(flat_data, conv_table_ref, job_config=conv_job_config)
                conv_job.result()
                print(f"Successfully loaded {len(flat_data)} conversations into {dataset_id}.deepseek_conversations")
            elif isinstance(data, dict):
                print(f"Root object keys: {list(data.keys())}")
                # Treat single dict as a row
                # Convert nested lists to json strings
                flat_row = {}
                for k, v in data.items():
                    if isinstance(v, (list, dict)):
                        flat_row[k] = json.dumps(v)
                    else:
                        flat_row[k] = str(v)
                
                conv_table_ref = client.dataset(dataset_id).table("deepseek_conversations")
                conv_job_config = bigquery.LoadJobConfig(
                    autodetect=True,
                    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
                )
                conv_job = client.load_table_from_json([flat_row], conv_table_ref, job_config=conv_job_config)
                conv_job.result()
                print(f"Successfully loaded 1 row into {dataset_id}.deepseek_conversations")
    except Exception as e:
        print(f"Error processing conversations.json: {e}")
else:
    print(f"Conversations file not found at: {conversations_path}")

# Step 3/3: Inspect user.json and load it
user_path = r"C:\Users\HP\Downloads\deepseek_data-2026-07-02 (1)\user.json"
print("\nStep 3/3: Inspecting and loading user.json...")
if os.path.exists(user_path):
    try:
        with open(user_path, 'r', encoding='utf-8') as f:
            user_data = json.load(f)
            print(f"Loaded user JSON. Type: {type(user_data)}")
            
            rows = []
            if isinstance(user_data, list):
                for user in user_data:
                    rows.append({k: (json.dumps(v) if isinstance(v, (list, dict)) else str(v)) for k, v in user.items()})
            elif isinstance(user_data, dict):
                rows.append({k: (json.dumps(v) if isinstance(v, (list, dict)) else str(v)) for k, v in user_data.items()})
                
            user_table_ref = client.dataset(dataset_id).table("deepseek_user")
            user_job_config = bigquery.LoadJobConfig(
                autodetect=True,
                write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            )
            user_job = client.load_table_from_json(rows, user_table_ref, job_config=user_job_config)
            user_job.result()
            print(f"Successfully loaded {len(rows)} user rows into {dataset_id}.deepseek_user")
    except Exception as e:
        print(f"Error processing user.json: {e}")
else:
    print(f"User file not found at: {user_path}")
