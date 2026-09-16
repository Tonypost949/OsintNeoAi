import hashlib
import json
import os
from datetime import datetime, timezone
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# BigQuery configuration
PROJECT_ID = "noble-beanbag-497411-m4"
DATASET_ID = "forensic_layers"
TABLE_ID = "genesis_ledger"

# Initialize BQ Client globally
try:
    bq_client = bigquery.Client(project=PROJECT_ID)
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
except Exception as e:
    print(f"Warning: BQ Client initialization failed: {e}")
    bq_client = None
    table_ref = None

STAGING_DIR = r"C:\OsintNeoAi\data\staging"
os.makedirs(STAGING_DIR, exist_ok=True)

class GenesisPayload(BaseModel):
    raw_text: str
    wallet_or_uid: str = "ANONYMOUS"
    source: str = "WEBHOOK_API"
    parent_receipt_hash: str = "0000000000000000000000000000000000000000000000000000000000000000"
    client_metadata: dict = {}

def extract_genesis_meta(text: str):
    genesis_type = "UNKNOWN"
    if text.strip().lower().startswith("my name is"):
        genesis_type = "BIO_DOSSIER"
    else:
        genesis_type = "CORP_ENTITY_WIKI"
        
    words = text.strip().split()
    target_entity = "Woodbridge Apartments" if "woodbridge" in text.lower() else (words[0] if words else "Unknown")
    
    return genesis_type, target_entity

def stream_to_bigquery_or_fallback(record: dict):
    """
    Appends the record to the append-only BigQuery table. If network or credentials
    fail, persists directly into the staging queue on disk.
    """
    written_to_bq = False
    
    if bq_client and table_ref:
        try:
            # Prepare row for BQ JSON streaming
            row_to_insert = {
                "receipt_hash": record["receipt_hash"],
                "parent_hash": record["parent_hash"],
                "timestamp_unix": record["timestamp_unix"],
                "timestamp": record["timestamp_iso"],
                "source_origin": record["source_origin"],
                "genesis_type": record["genesis_type"],
                "target_entity": record["target_entity"],
                "raw_payload": record["raw_payload"],
                "ledger_value": record["ledger_value"],
                "verification_status": record["verification_status"],
                "enrichment_status": record["enrichment_status"],
                "metadata": json.dumps(record.get("metadata", {}))
            }
            
            errors = bq_client.insert_rows_json(table_ref, [row_to_insert])
            if not errors:
                written_to_bq = True
            else:
                print(f"[!] BQ Streaming Errors: {errors}")
        except GoogleAPIError as g_err:
            print(f"[!] BigQuery Insert Failure: {g_err}")
        except Exception as e:
            print(f"[!] General Stream Failure: {e}")

    # Fallback to local staging for autonomous background pick-up
    staging_file = os.path.join(STAGING_DIR, f"{record['receipt_hash']}.json")
    record["persisted_to_bq"] = written_to_bq
    with open(staging_file, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)

@app.post("/api/genesis/ingest", status_code=202)
async def genesis_ingest(payload: GenesisPayload, background_tasks: BackgroundTasks):
    cleaned_text = payload.raw_text.strip()
    if not cleaned_text:
        raise HTTPException(status_code=400, detail="Data payload cannot be empty.")
        
    now = datetime.now(timezone.utc)
    timestamp_unix = int(now.timestamp())
    timestamp_iso = now.isoformat()
    
    # 1. Generate SHA-256 Receipt Hash
    hash_seed = f"{cleaned_text}:{timestamp_unix}:{payload.wallet_or_uid}".encode("utf-8")
    sha256_hash = hashlib.sha256(hash_seed).hexdigest()
    
    # 2. Extract Type & Entity Anchor
    genesis_type, target_entity = extract_genesis_meta(cleaned_text)
    
    # 3. Construct Zero-Value Immutable Ledger Block
    ledger_entry = {
        "receipt_hash": sha256_hash,
        "parent_hash": payload.parent_receipt_hash,
        "timestamp_unix": timestamp_unix,
        "timestamp_iso": timestamp_iso,
        "source_origin": payload.source,
        "genesis_type": genesis_type,
        "target_entity": target_entity,
        "raw_payload": cleaned_text,
        "ledger_value": 0.00,  # Strict zero-value baseline
        "verification_status": "UNVERIFIED_GENESIS",
        "enrichment_status": "PENDING_AUTONOMOUS_REVIEW",
        "metadata": {
            "wallet": payload.wallet_or_uid,
            "client_meta": payload.client_metadata,
            "pipeline": "TASK-084-WIF-INGEST"
        }
    }
    
    # 4. Offload Ledger Commit to Background Task (instant client return)
    background_tasks.add_task(stream_to_bigquery_or_fallback, ledger_entry)
    
    # 5. Return Receipt Immediately to Caller
    return {
        "status": "ACCEPTED",
        "receipt_hash": f"0x{sha256_hash}",
        "timestamp": timestamp_iso,
        "genesis_type": genesis_type,
        "target_entity": target_entity,
        "ledger_value": "$0.00",
        "chain_status": "COMMITTED_UNMINED_BLOCK",
        "verification_check_url": f"/api/ledger/receipt/0x{sha256_hash}"
    }

@app.get("/api/ledger/receipt/{receipt_hash}")
async def get_receipt_status(receipt_hash: str):
    clean_hash = receipt_hash.replace("0x", "")
    staging_file = os.path.join(STAGING_DIR, f"{clean_hash}.json")
    
    # Check local staging first
    if os.path.exists(staging_file):
        try:
            with open(staging_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            return {
                "receipt_hash": f"0x{clean_hash}",
                "ledger_value": data.get("ledger_value", 0.0),
                "verification_status": data.get("verification_status", "UNKNOWN"),
                "enrichment_status": data.get("enrichment_status", "PENDING_AUTONOMOUS_REVIEW"),
                "persisted_to_bq": data.get("persisted_to_bq", False),
                "timestamp": data.get("timestamp_iso")
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading receipt data: {str(e)}")
            
    # Query BigQuery directly if cleared from staging
    if bq_client and table_ref:
        query = f"""
        SELECT receipt_hash, timestamp, target_entity, ledger_value, verification_status, enrichment_status
        FROM `{table_ref}`
        WHERE receipt_hash = @hash
        LIMIT 1
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("hash", "STRING", clean_hash)
            ]
        )
        query_job = bq_client.query(query, job_config=job_config)
        results = list(query_job.result())
        
        if results:
            row = results[0]
            return {
                "receipt_hash": f"0x{row.receipt_hash}",
                "ledger_value": float(row.ledger_value),
                "verification_status": row.verification_status,
                "enrichment_status": row.enrichment_status,
                "persisted_to_bq": True,
                "timestamp": row.timestamp.isoformat()
            }
            
    raise HTTPException(status_code=404, detail="Receipt hash not found on ledger.")

if __name__ == "__main__":
    uvicorn.run("dynamic_genesis_webhook:app", host="0.0.0.0", port=10001, reload=True)
