import os
import json
import time
import shutil
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError

BQ_PROJECT = os.getenv("BQ_PROJECT_ID", "noble-beanbag-497411-m4")
BQ_DATASET = os.getenv("BQ_DATASET_ID", "forensic_layers")
BQ_TABLE = os.getenv("BQ_TABLE_ID", "genesis_ledger")
TABLE_REF = f"{BQ_PROJECT}.{BQ_DATASET}.{BQ_TABLE}"

STAGING_DIR = r"C:\OsintNeoAi\data\staging"
ARCHIVE_DIR = r"C:\OsintNeoAi\data\staging\archived_synced"
os.makedirs(ARCHIVE_DIR, exist_ok=True)

def sweep_and_sync():
    print(f"[*] BigQuery Sync Worker Active. Monitoring: {STAGING_DIR}")
    try:
        client = bigquery.Client(project=BQ_PROJECT)
    except Exception as e:
        print(f"[!] BigQuery Client init failed: {e}. Worker will poll local queue.")
        client = None

    while True:
        pending_files = [f for f in os.listdir(STAGING_DIR) if f.endswith(".json")]
        
        for filename in pending_files:
            file_path = os.path.join(STAGING_DIR, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    record = json.load(f)
                
                synced = False
                if client:
                    try:
                        job_config = bigquery.LoadJobConfig(
                            write_disposition="WRITE_APPEND",
                            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
                        )
                        # Load via free-tier compatible LoadJob
                        load_job = client.load_table_from_json([record], TABLE_REF, job_config=job_config)
                        load_job.result()
                        synced = True
                        print(f"[+] SYNCED TO BIGQUERY LEDGER: {record.get('receipt_hash')}")
                    except Exception as bq_err:
                        print(f"[!] BQ Load Job error on {filename}: {bq_err}")
                
                # Move file to archive regardless after local confirmation
                archive_path = os.path.join(ARCHIVE_DIR, filename)
                shutil.move(file_path, archive_path)
                print(f"[+] Moved {filename} to {archive_path}")
                
            except Exception as err:
                print(f"[!] Error processing {filename}: {err}")
                
        time.sleep(5)

if __name__ == "__main__":
    sweep_and_sync()
