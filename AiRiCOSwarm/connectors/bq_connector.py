"""BigQuery Database Connector for AiRiCOSwarm."""

from google.cloud import bigquery
from google.oauth2.credentials import Credentials
import os
from typing import List, Dict, Any, Optional

class BigQueryConnector:
    def __init__(self, project_id: str = "noble-beanbag-497411-m4", token_path: Optional[str] = None):
        self.project_id = project_id
        self.client = None
        self._init_client(token_path)

    def _init_client(self, token_path: Optional[str] = None):
        if not token_path:
            token_path = os.path.join(os.path.dirname(__file__), '..', '..', 'agent', 'token.json')
            
        try:
            if token_path and os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path)
                self.client = bigquery.Client(project=self.project_id, credentials=creds)
            else:
                self.client = bigquery.Client(project=self.project_id)
            print("[BQ] BigQuery Client connected.")
        except Exception as e:
            print(f"[BQ] Warning initializing client: {e}")

    def query(self, sql: str) -> List[Dict[str, Any]]:
        if not self.client:
            return []
        try:
            job = self.client.query(sql)
            return [dict(row) for row in job.result()]
        except Exception as e:
            print(f"[BQ] Query execution error: {e}")
            return []

    def record_finding(self, title: str, description: str, links: List[str] = []) -> bool:
        if not self.client:
            return False
        table_id = f"{self.project_id}.ai_sandbox.findings"
        links_str = ", ".join(links)
        sql = f"""
            INSERT INTO `{table_id}` (title, description, evidence_links, timestamp)
            VALUES (
                '{title.replace("'", "\\'")}',
                '{description.replace("'", "\\'")}',
                '{links_str.replace("'", "\\'")}',
                CURRENT_TIMESTAMP()
            )
        """
        try:
            self.client.query(sql).result()
            return True
        except Exception as e:
            print(f"[BQ] Record finding error: {e}")
            return False
