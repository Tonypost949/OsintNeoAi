import hashlib
import os
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from google.cloud import bigquery
from google.auth import identity_pool

class MasterLedgerService:
    def __init__(self, project_id: str, dataset_id: str = "osint_engine", table_id: str = "master_ledger"):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id = table_id
        self.table_ref = f"{project_id}.{dataset_id}.{table_id}"
        
        # Load credentials via Workload Identity Federation (No static keys)
        wif_config_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "config/gcp_wif_config.json")
        self.credentials = identity_pool.Credentials.from_info_file(wif_config_path)
        self.client = bigquery.Client(project=project_id, credentials=self.credentials)

    @staticmethod
    def calculate_sha256(file_bytes: bytes) -> str:
        """Point-of-Upload SHA-256 Hashing [TASK-083]"""
        hasher = hashlib.sha256()
        hasher.update(file_bytes)
        return hasher.hexdigest()

    def record_asset(
        self,
        file_bytes: bytes,
        miner_signature: str,
        title: str,
        domain_tags: List[str],
        description: Optional[str] = None,
        raw_payload_uri: Optional[str] = None,
        parent_hash: Optional[str] = None,
        version_id: int = 1
    ) -> Dict[str, Any]:
        """
        Appends an immutable block to the Master Ledger.
        Overwrites are strictly banned; all modifications create new version layers [TASK-077].
        """
        # 1. Cryptographic hashing at exact upload time
        asset_hash = self.calculate_sha256(file_bytes)
        
        # 2. Construct row conforming to master_ledger DDL
        row = {
            "asset_hash": asset_hash,
            "parent_hash": parent_hash,
            "miner_signature": miner_signature,
            "domain_tags": [tag.upper() for tag in domain_tags],
            "title": title,
            "description": description,
            "raw_payload_uri": raw_payload_uri,
            "version_id": version_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True
        }

        # 3. Append-only insert to BigQuery
        errors = self.client.insert_rows_json(self.table_ref, [row])
        if errors:
            raise RuntimeError(f"Failed to append to BigQuery Master Ledger: {errors}")

        return row

