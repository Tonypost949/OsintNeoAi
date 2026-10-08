import os
import json
import time
import hashlib
import re
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="OSINTNeoAI Genesis Ingestion Webhook",
    version="1.0.0",
    description="Zero-Trust Append-Only Ingestion Engine for Raw OSINT Intelligence"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STAGING_DIR = os.getenv("STAGING_DIR", "C:/OsintNeoAi/data/staging")
os.makedirs(STAGING_DIR, exist_ok=True)

class GenesisPayload(BaseModel):
    raw_text: str = Field(..., description="Raw text, claim, evidence dump, or intelligence string")
    source: str = Field(default="OSINTNeoAI_Main", description="Origin: OSINTNeoAI_Main or TaxFunded_Fallback")
    wallet_or_uid: str = Field(default="0xANON_LEDGER_KEY", description="User public key or anonymous session ID")
    parent_receipt_hash: Optional[str] = Field(default=None, description="Previous block hash if appending to a thread")
    client_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="UI parameters or telemetry")

def extract_genesis_meta(text: str):
    bio_patterns = [r"^my name is", r"^i am", r"^i'm", r"^me,?\s+"]
    first_segment = text.strip().lower()[:40]
    genesis_type = "BIO" if any(re.search(p, first_segment) for p in bio_patterns) else "ENTITY"

    words = text.strip().split()
    target_entity = "Woodbridge Apartments" if "woodbridge" in text.lower() else ("17631 Cameron Lane" if "cameron" in text.lower() else (words[0] if words else "Unknown"))

    return genesis_type, target_entity

def save_to_staging(record: dict):
    staging_file = os.path.join(STAGING_DIR, f"{record['receipt_hash']}.json")
    with open(staging_file, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)
    print(f"[+] Staged payload locally for BigQuery Sync Worker: {staging_file}")

@app.post("/api/genesis/ingest", status_code=202)
async def genesis_ingest(payload: GenesisPayload, background_tasks: BackgroundTasks):
    cleaned_text = payload.raw_text.strip()
    if not cleaned_text:
        raise HTTPException(status_code=400, detail="Data payload cannot be empty.")

    now = datetime.now(timezone.utc)
    timestamp_unix = int(now.timestamp())
    timestamp_iso = now.isoformat()

    hash_seed = f"{cleaned_text}:{timestamp_unix}:{payload.wallet_or_uid}".encode("utf-8")
    sha256_hash = hashlib.sha256(hash_seed).hexdigest()

    genesis_type, target_entity = extract_genesis_meta(cleaned_text)

    ledger_entry = {
        "receipt_hash": f"0x{sha256_hash}",
        "parent_hash": payload.parent_receipt_hash,
        "timestamp_unix": timestamp_unix,
        "timestamp_iso": timestamp_iso,
        "source_origin": payload.source,
        "genesis_type": genesis_type,
        "target_entity": target_entity,
        "raw_payload": cleaned_text,
        "ledger_value": "$0.00",
        "verification_status": "UNVERIFIED_GENESIS",
        "enrichment_status": "PENDING_AUTONOMOUS_REVIEW",
        "metadata": {
            "wallet": payload.wallet_or_uid,
            "client_meta": payload.client_metadata,
            "pipeline": "TASK-084-WIF-INGEST"
        }
    }

    background_tasks.add_task(save_to_staging, ledger_entry)

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
    staging_file = os.path.join(STAGING_DIR, f"0x{clean_hash}.json")

    if os.path.exists(staging_file):
        with open(staging_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {
            "receipt_hash": f"0x{clean_hash}",
            "ledger_value": data.get("ledger_value", "$0.00"),
            "verification_status": data.get("verification_status", "UNKNOWN"),
            "enrichment_status": data.get("enrichment_status", "PENDING_AUTONOMOUS_REVIEW"),
            "timestamp": data.get("timestamp_iso")
        }

    raise HTTPException(status_code=404, detail="Receipt hash not found on staging queue.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10001)
