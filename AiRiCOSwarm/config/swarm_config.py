"""AiRiCOSwarm Configuration Module
Defines models, API keys, BigQuery datasets, and swarm operational parameters.
"""

import os
from typing import Dict, Any, List

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "noble-beanbag-497411-m4")

BIGQUERY_DATASETS = {
    "gmail_index": f"{GCP_PROJECT_ID}.national_audits.gmail_index",
    "drive_index": f"{GCP_PROJECT_ID}.national_audits.drive_file_index",
    "photos_index": f"{GCP_PROJECT_ID}.national_audits.google_photos_index",
    "fca_timeline": f"{GCP_PROJECT_ID}.forensic_layers.fca_timeline",
    "state_records": f"{GCP_PROJECT_ID}.national_audits.all_state_records",
    "findings_sandbox": f"{GCP_PROJECT_ID}.ai_sandbox.findings"
}

GCS_VAULT_BUCKET = os.getenv("GCS_VAULT_BUCKET", "osint-ai-evidence-vault-m4")

SWARM_MODELS: Dict[str, Any] = {
    "primary": {
        "provider": "google",
        "model_id": "gemini-2.5-flash",
        "api_key": os.getenv("GEMINI_API_KEY", "")
    },
    "reasoning": {
        "provider": "google",
        "model_id": "gemini-1.5-pro",
        "api_key": os.getenv("GEMINI_API_KEY", "")
    },
    "local_fallback": {
        "provider": "openai_compatible",
        "model_id": "llama3",
        "base_url": os.getenv("LOCAL_LLM_URL", "http://127.0.0.1:11434/v1"),
        "api_key": "NotRequired"
    },
    "antigravity_byok": {
        "provider": "customendpoint",
        "model_id": "gemini-3-flash-agent",
        "base_url": "http://127.0.0.1:8420/v1",
        "api_key": "NotRequired"
    }
}

RICO_PREDICATE_KEYWORDS: List[str] = [
    "indictment", "conviction", "guilty plea", "bribery", "rico",
    "qui tam", "false claims", "wire fraud", "mail fraud", "money laundering",
    "kickback", "bid rigging", "straw donor", "shell company", "alter ego",
    "forfeiture", "embezzlement", "conspiracy", "hexavalent chromium",
    "environmental violation", "chdo grant fraud", "hud diversion",
    "subcontractor skimming", "co-mingled funds", "apn falsification",
    "cross-border", "offshore transfer", "philippines", "manila", "smuggling"
]
