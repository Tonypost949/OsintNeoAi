import logging
import json
from typing import Dict, Any
from core.AG2OSINTNEOMAXX.ai_worker_router import AIWorkerRouter
from core.AG2OSINTNEOMAXX.ledger_service import MasterLedgerService

logger = logging.getLogger("BackgroundConsumer")
logging.basicConfig(level=logging.INFO)

class DeepExtractionConsumer:
    def __init__(self, project_id: str):
        self.router = AIWorkerRouter(project_id=project_id)
        self.ledger = MasterLedgerService(project_id=project_id)

    def process_queue_payload(self, queue_payload: Dict[str, Any]) -> None:
        """
        Consumes the heavy payload enqueued by the Fast Triage worker.
        Executes Deep Extraction and appends version 2 to the ledger.
        """
        asset_hash = queue_payload["asset_hash"]
        full_text = queue_payload["full_text"]
        miner_signature = queue_payload["miner_signature"]
        domain_tags = queue_payload["domain_tags"]
        
        logger.info(f"Starting heavy extraction for asset: {asset_hash}")

        # 1. Execute Heavy AI Parsing (Legal schemas, Entity Graphs)
        deep_meta = self.router.process_deep_extraction(full_text=full_text, asset_hash=asset_hash)
        
        # 2. Defect Hook: Alert if missing official government links
        if deep_meta.get("defect_detected"):
            logger.warning(f"DEFECT LOGGED: {deep_meta.get('defect_notes')}")
            # Here you would trigger the automated admin alert / defect bounty routing

        # 3. Construct enriched description
        enriched_description = json.dumps({
            "legal_citations": deep_meta.get("legal_citations", []),
            "entity_graph": deep_meta.get("entity_graph", {})
        })

        # 4. Append Event Sourced Version 2 to BigQuery 
        # By referencing the original asset_hash as parent_hash, we maintain the UTXO lineage.
        self.ledger.record_asset(
            file_bytes=full_text.encode('utf-8'), # Using text bytes for the appended state
            miner_signature=miner_signature,
            title=f"Enriched: {queue_payload.get('title', 'Evidence')}",
            domain_tags=domain_tags,
            description=enriched_description,
            parent_hash=asset_hash, 
            version_id=2
        )
        
        logger.info(f"Successfully appended Version 2 for asset: {asset_hash}")
