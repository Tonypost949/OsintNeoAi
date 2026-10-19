import logging
import requests
import os
from typing import List, Dict, Any
from datetime import datetime, timezone
from google.cloud import bigquery
from google.auth import identity_pool

logger = logging.getLogger("BulkCachingQueue")
logging.basicConfig(level=logging.INFO)

class BulkCachingQueue:
    def __init__(self, project_id: str):
        self.project_id = project_id
        # Dedicated cache table to keep the Master Ledger clean
        self.table_ref = f"{project_id}.osint_engine.taxfunded_cache"
        
        # Leverages the zero-trust WIF bridge established earlier
        wif_config_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "config/gcp_wif_config.json")
        self.credentials = identity_pool.Credentials.from_info_file(wif_config_path)
        self.bq_client = bigquery.Client(project=project_id, credentials=self.credentials)

    def execute_off_peak_sync(self) -> None:
        """
        [TASK-079] Downloads bulk datasets during off-peak hours to avoid the Rate-Limit Guillotine.
        Routes subsequent user searches to BigQuery instead of pinging live APIs.
        """
        logger.info("Executing off-peak bulk data sync for TaxFunded APIs...")
        
        # Example external API (ProPublica Nonprofit Explorer)
        target_url = "https://projects.propublica.org/nonprofits/api/v2/search.json?q=grant"
        
        try:
            response = requests.get(target_url, timeout=45)
            response.raise_for_status()
            payload = response.json()
            
            rows_to_insert = self._parse_and_format(payload.get("organizations", []))
            
            if rows_to_insert:
                errors = self.bq_client.insert_rows_json(self.table_ref, rows_to_insert)
                if errors:
                    logger.error(f"BigQuery caching failed: {errors}")
                else:
                    logger.info(f"Successfully bulk-cached {len(rows_to_insert)} external records.")
                    
        except requests.exceptions.RequestException as e:
            logger.error(f"External API Rate-Limit/Connection Error: {e}")

    def _parse_and_format(self, raw_orgs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Formats the external payload into the BigQuery cache schema."""
        formatted = []
        for org in raw_orgs:
            formatted.append({
                "ein": org.get("ein"),
                "entity_name": org.get("name"),
                "city": org.get("city"),
                "source_api": "PROPUBLICA",
                "cached_timestamp": datetime.now(timezone.utc).isoformat()
            })
        return formatted
