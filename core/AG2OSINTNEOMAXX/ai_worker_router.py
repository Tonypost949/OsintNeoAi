import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from google import genai
from google.genai import types
from core.AG2OSINTNEOMAXX.ledger_service import MasterLedgerService

logger = logging.getLogger("AIWorkerRouter")
logging.basicConfig(level=logging.INFO)

class AIWorkerRouter:
    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID", "osint-neo-ai")
        # Initialize Gemini API Client using environment credentials / WIF
        self.client = genai.Client()
        self.ledger_service = MasterLedgerService(project_id=self.project_id)
        
        # Micro-worker model definitions [TASK-082]
        self.fast_model = "gemini-2.5-flash"
        self.deep_model = "gemini-1.5-pro"

    def triage_fast_metadata(self, sample_text: str) -> Dict[str, Any]:
        """
        Tier 1: High-speed triage worker (The Receptionist) [TASK-082].
        Extracts title, short description, and primary domain tags instantly.
        """
        prompt = (
            "You are the fast triage worker for an open-source intelligence and taxpayer audit engine.\n"
            "Analyze the following evidence sample (first pages/summary) and return JSON strictly adhering to:\n"
            "{\n"
            "  \"title\": \"Direct, descriptive investigative title\",\n"
            "  \"description\": \"1-2 sentence executive summary of the finding\",\n"
            "  \"suggested_tags\": [\"TAX-FUNDED\" or \"OSINT\" or \"MED\" or \"LEGAL\"]\n"
            "}\n\n"
            f"EVIDENCE SAMPLE:\n{sample_text[:4000]}"
        )

        response = self.client.models.generate_content(
            model=self.fast_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )

        try:
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Failed to parse fast triage JSON: {e}")
            return {
                "title": "Unclassified Ingested Evidence",
                "description": sample_text[:150].strip() + "...",
                "suggested_tags": ["OSINT"]
            }

    def process_deep_extraction(self, full_text: str, asset_hash: str) -> Dict[str, Any]:
        """
        Tier 2: Background Heavy Worker [TASK-082].
        Executes statutory legal extraction and entity mapping per Master Architecture.
        """
        prompt = (
            "You are an expert legal and corporate forensic auditor.\n"
            "Examine this full public-records/investigative document and extract:\n"
            "1. Legal citations adhering to the schema:\n"
            "   - title, code, year, type_of_law, jurisdiction, jurisdiction_type (Federal/State/County/City),\n"
            "     government_type, tax_funded_flag (true/false), one_sentence_summary, official_url\n"
            "2. Entity graph relationships:\n"
            "   - ngos, corporate_officers, registered_addresses, parent_companies\n\n"
            "Return valid JSON:\n"
            "{\n"
            "  \"legal_citations\": [...],\n"
            "  \"entity_graph\": {\n"
            "    \"ngos\": [],\n"
            "    \"officers\": [],\n"
            "    \"addresses\": [],\n"
            "    \"parent_entities\": []\n"
            "  },\n"
            "  \"defect_detected\": false,\n"
            "  \"defect_notes\": \"\"\n"
            "}\n\n"
            f"FULL DOCUMENT TEXT:\n{full_text}"
        )

        response = self.client.models.generate_content(
            model=self.deep_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )

        return json.loads(response.text)

    def route_incoming_document(
        self,
        file_bytes: bytes,
        full_text: str,
        miner_signature: str,
        user_tags: Optional[List[str]] = None,
        parent_hash: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Orchestration pipeline:
        1. Immediate Fast Triage via Flash (Instant user response) [TASK-082].
        2. Append initial Block Layer to BigQuery via WIF [TASK-077, TASK-083].
        3. Enqueue Deep Extraction for asynchronous background processing.
        """
        # Step 1: Instant Fast Triage
        triage_meta = self.triage_fast_metadata(full_text)
        
        # Merge tags
        final_tags = set(user_tags or [])
        final_tags.update(triage_meta.get("suggested_tags", []))
        if not final_tags:
            final_tags.add("OSINT")

        # Step 2: Immediate Append-Only Ledger Entry (Version 1)
        ledger_entry = self.ledger_service.record_asset(
            file_bytes=file_bytes,
            miner_signature=miner_signature,
            title=triage_meta.get("title", "Evidence Ingestion"),
            domain_tags=list(final_tags),
            description=triage_meta.get("description"),
            parent_hash=parent_hash,
            version_id=1
        )

        # Step 3: Payload packaged for Async Queue (Azure Service Bus / Celery / Worker Pool)
        queue_payload = {
            "asset_hash": ledger_entry["asset_hash"],
            "full_text": full_text,
            "miner_signature": miner_signature,
            "domain_tags": list(final_tags),
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        logger.info(f"Asset {ledger_entry['asset_hash'][:10]}... logged. Heavy job enqueued.")
        
        return {
            "status": "RECORDED_AND_QUEUED",
            "asset_hash": ledger_entry["asset_hash"],
            "title": ledger_entry["title"],
            "domain_tags": ledger_entry["domain_tags"],
            "version_id": ledger_entry["version_id"],
            "queue_payload": queue_payload
        }
