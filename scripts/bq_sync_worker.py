import os
import json
import time
import shutil
from google.cloud import bigquery

BQ_PROJECT = "noble-beanbag-497411-m4"
TABLE_REF = f"{BQ_PROJECT}.forensic_layers.genesis_ledger"

STAGING_DIR = r"C:\OsintNeoAi\data\staging"
ARCHIVE_DIR = r"C:\OsintNeoAi\data\staging\archived_synced"

os.makedirs(ARCHIVE_DIR, exist_ok=True)

def sweep_and_sync():
    client = bigquery.Client(project=BQ_PROJECT)
    print(f"[*] Sync Worker Active. Monitoring: {STAGING_DIR}")
    
    while True:
        # Scan for pending JSON payloads
        pending_files = [f for f in os.listdir(STAGING_DIR) if f.endswith(".json")]
        for filename in pending_files:
            file_path = os.path.join(STAGING_DIR, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    record = json.load(f)
                    
                # Format for BQ streaming
                row_to_insert = {
                    "receipt_hash": record["receipt_hash"],
                    "parent_hash": record.get("parent_hash"),
                    "timestamp_unix": record.get("timestamp_unix"),
                    "timestamp": record["timestamp_iso"],
                    "source_origin": record.get("source_origin", "UNKNOWN"),
                    "genesis_type": record.get("genesis_type", "UNKNOWN"),
                    "target_entity": record.get("target_entity"),
                    "raw_payload": record["raw_payload"],
                    "ledger_value": record["ledger_value"],
                    "verification_status": record["verification_status"],
                    "enrichment_status": record["enrichment_status"],
                    "metadata": json.dumps(record.get("metadata", {}))
                }
                
                # Push to Ledger using LoadJob (Free Tier compatible instead of Streaming Insert)
                job_config = bigquery.LoadJobConfig(source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON)
                job = client.load_table_from_json([row_to_insert], TABLE_REF, job_config=job_config)
                job.result() # Wait for the job to complete
                errors = job.errors

                if not errors:
                    print(f"[+] SYNCED TO LEDGER: {record['receipt_hash']}")
                    # Move to archive so we don't double-process
                    shutil.move(file_path, os.path.join(ARCHIVE_DIR, filename))
                else:
                    print(f"[!] Sync Failed for {filename}: {errors}")
            except Exception as e:
                print(f"[!] Error processing {filename}: {e}")
                
        # Sleep before next sweep (e.g., 10 seconds)
        time.sleep(10)

if __name__ == "__main__":
    sweep_and_sync()
