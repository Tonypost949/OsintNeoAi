import os
import json
import hashlib
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any
from google.cloud import bigquery
from google.auth import identity_pool

logger = logging.getLogger("AutonomousTaskWorker")
logging.basicConfig(level=logging.INFO)

class AutonomousTaskWorker:
    def __init__(self, project_id: str = None):
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID", "osint-neo-ai")
        self.tasks_table = f"{self.project_id}.osint_engine.suggestive_tasks"
        self.master_table = f"{self.project_id}.osint_engine.master_ledger"

        # Zero-Trust WIF Bridge Authentication
        wif_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "config/gcp_wif_config.json")
        self.credentials = identity_pool.Credentials.from_info_file(wif_path)
        self.client = bigquery.Client(project=self.project_id, credentials=self.credentials)

    @staticmethod
    def _gen_task_id(task_type: str, key_factor: str) -> str:
        """Generates an idempotent SHA-256 ID to prevent duplicate tasks across CRON runs."""
        seed = f"{task_type}:{key_factor}"
        return hashlib.sha256(seed.encode("utf-8")).hexdigest()

    def scan_disconnected_entities(self) -> List[Dict[str, Any]]:
        """Primary Directive: Identifies unlinked entities spanning multiple investigations."""
        query = f"""
        WITH ActiveBlocks AS (
          SELECT asset_hash, miner_signature, title, SAFE.PARSE_JSON(description) AS parsed_desc
          FROM `{self.master_table}`
          WHERE version_id = 2 AND is_active = TRUE
        ),
        ExtractedEntities AS (
          SELECT
            asset_hash, miner_signature, entity_type,
            TRIM(LOWER(entity_name)) AS normalized_entity,
            entity_name AS original_entity_name
          FROM ActiveBlocks,
          UNNEST([
            STRUCT('NGO' AS entity_type, JSON_VALUE_ARRAY(parsed_desc.entity_graph.ngos) AS items),
            STRUCT('OFFICER' AS entity_type, JSON_VALUE_ARRAY(parsed_desc.entity_graph.officers) AS items)
          ]),
          UNNEST(items) AS entity_name
          WHERE entity_name IS NOT NULL AND LENGTH(TRIM(entity_name)) > 2
        )
        SELECT
          normalized_entity,
          original_entity_name,
          entity_type,
          COUNT(DISTINCT asset_hash) AS asset_count,
          ARRAY_AGG(DISTINCT asset_hash) AS related_asset_hashes,
          ARRAY_AGG(DISTINCT miner_signature) AS related_miners
        FROM ExtractedEntities
        GROUP BY normalized_entity, original_entity_name, entity_type
        HAVING asset_count > 1
        LIMIT 50
        """
        rows = self.client.query(query).result()
        tasks = []

        for row in rows:
            task_id = self._gen_task_id("DISCONNECTED_ENTITY", row.normalized_entity)
            prompt = (
                f"Entity '{row.original_entity_name}' appears in {row.asset_count} separate cases without a direct link. "
                "Submit cross-verifying FOIA documentation to establish the chain of custody."
            )
            tasks.append({
                "task_id": task_id,
                "task_type": "DISCONNECTED_ENTITY",
                "priority_score": min(row.asset_count * 2, 10),
                "target_asset_hash": row.related_asset_hashes[0],
                "miner_signature": row.related_miners[0],
                "title": f"Missing Link: {row.original_entity_name}",
                "prompt_message": prompt,
                "suggested_action": "Search public records for overlapping contracts or grants linking these cases.",
                "entity_payload": json.dumps({
                    "entity": row.original_entity_name,
                    "type": row.entity_type,
                    "connected_assets": row.related_asset_hashes
                }),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "is_resolved": False
            })
        return tasks

    def scan_data_anomalies(self) -> List[Dict[str, Any]]:
        """Secondary Directive: Flags missing legal citations or detected link defects."""
        query = f"""
        SELECT
          asset_hash AS target_asset_hash,
          miner_signature,
          title,
          CASE
            WHEN ARRAY_LENGTH(JSON_VALUE_ARRAY(SAFE.PARSE_JSON(description).legal_citations)) = 0 
              OR SAFE.PARSE_JSON(description).legal_citations IS NULL THEN 'MISSING_CITATION'
            WHEN JSON_VALUE(SAFE.PARSE_JSON(description).defect_detected) = 'true' THEN 'BROKEN_LINK'
            ELSE 'DATA_DEFECT'
          END AS task_type,
          JSON_VALUE(SAFE.PARSE_JSON(description).defect_notes) AS defect_notes
        FROM `{self.master_table}`
        WHERE version_id = 2 AND is_active = TRUE
          AND (
            ARRAY_LENGTH(JSON_VALUE_ARRAY(SAFE.PARSE_JSON(description).legal_citations)) = 0
            OR SAFE.PARSE_JSON(description).legal_citations IS NULL
            OR JSON_VALUE(SAFE.PARSE_JSON(description).defect_detected) = 'true'
          )
        LIMIT 50
        """
        rows = self.client.query(query).result()
        tasks = []

        for row in rows:
            task_id = self._gen_task_id(row.task_type, row.target_asset_hash)
            if row.task_type == "MISSING_CITATION":
                msg = f"Evidence '{row.title}' was processed with zero valid statutory legal citations."
                action = "Upload statutory references (USC, CFR, or State Code) to strengthen bounty standing."
                priority = 6
            else:
                msg = f"Evidence contains defects or broken source links: {row.defect_notes or 'Unreachable URL'}."
                action = "Submit an archive.org link or replacement primary source."
                priority = 8

            tasks.append({
                "task_id": task_id,
                "task_type": row.task_type,
                "priority_score": priority,
                "target_asset_hash": row.target_asset_hash,
                "miner_signature": row.miner_signature,
                "title": f"Hygiene Alert: {row.title[:30]}...",
                "prompt_message": msg,
                "suggested_action": action,
                "entity_payload": json.dumps({"defect_notes": row.defect_notes}),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "is_resolved": False
            })
        return tasks

    def run_cron_cycle(self) -> int:
        """Executes full scan and batches deduplicated task inserts."""
        logger.info("Executing Autonomous Task Worker batch cycle...")
        tasks = self.scan_disconnected_entities() + self.scan_data_anomalies()

        if not tasks:
            logger.info("No actionable graph gaps or anomalies detected.")
            return 0

        errors = self.client.insert_rows_json(self.tasks_table, tasks)
        if errors:
            logger.error(f"Failed to insert suggestive tasks: {errors}")
            raise RuntimeError(f"BigQuery task insertion failed: {errors}")

        logger.info(f"Successfully published {len(tasks)} tasks to the suggestive queue.")
        return len(tasks)

if __name__ == "__main__":
    worker = AutonomousTaskWorker()
    worker.run_cron_cycle()
