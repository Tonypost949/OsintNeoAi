"""EvidenceIngestionAgent: Multi-vector ingestion across exact BigQuery tables & local intelligence caches."""

import os
import json
from typing import Dict, Any, List

class EvidenceIngestionAgent:
    def __init__(self, bq_connector):
        self.bq = bq_connector

    def search_evidence(self, term: str, limit: int = 150) -> List[Dict[str, Any]]:
        safe_term = term.replace("'", "\\'")
        results = []
        term_lower = term.lower()
        alt_term = "philippines" if "phillipines" in term_lower else "phillipines"
        
        # 1. Query: takeout_mail_metadata
        query_mail = f"""
            SELECT CAST(sent_timestamp AS STRING) AS date, from_address AS sender, subject, to_addresses AS snippet 
            FROM `noble-beanbag-497411-m4.national_audits.takeout_mail_metadata`
            WHERE LOWER(subject) LIKE '%{safe_term.lower()}%'
               OR LOWER(subject) LIKE '%philippines%'
               OR LOWER(to_addresses) LIKE '%{safe_term.lower()}%'
            LIMIT {limit}
        """
        hits_mail = self.bq.query(query_mail)
        if hits_mail:
            results.extend(hits_mail)

        # 2. Query: local_scan_extracted_text
        query_text = f"""
            SELECT source_folder AS date, path AS sender, SUBSTR(path, -50) AS subject, extracted_text AS snippet 
            FROM `noble-beanbag-497411-m4.national_audits.local_scan_extracted_text`
            WHERE LOWER(extracted_text) LIKE '%{safe_term.lower()}%'
               OR LOWER(extracted_text) LIKE '%philippines%'
               OR LOWER(path) LIKE '%{safe_term.lower()}%'
            LIMIT {limit}
        """
        hits_text = self.bq.query(query_text)
        if hits_text:
            results.extend(hits_text)

        # 3. Query: local_scan_matches
        query_matches = f"""
            SELECT source_folder AS date, type AS sender, value AS subject, matched_value_or_score AS snippet 
            FROM `noble-beanbag-497411-m4.national_audits.local_scan_matches`
            WHERE LOWER(value) LIKE '%{safe_term.lower()}%'
               OR LOWER(matched_value_or_score) LIKE '%{safe_term.lower()}%'
               OR LOWER(value) LIKE '%philippines%'
            LIMIT {limit}
        """
        hits_matches = self.bq.query(query_matches)
        if hits_matches:
            results.extend(hits_matches)

        # 4. Local intelligence JSON fallback search
        local_files = [
            "gmail_amd949609_hits.json",
            "gmail_govt_responses_hits.json",
            "nodes.json",
            "control_clusters.json"
        ]

        for fname in local_files:
            if os.path.exists(fname):
                try:
                    with open(fname, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            for item in data:
                                text_repr = json.dumps(item).lower()
                                if term_lower in text_repr or alt_term in text_repr:
                                    results.append({
                                        "date": str(item.get("date", item.get("createdTime", "N/A"))),
                                        "sender": str(item.get("from", item.get("sender", item.get("source", "Local Cache")))),
                                        "subject": str(item.get("subject", item.get("name", item.get("label", "Local Hit")))),
                                        "snippet": str(item.get("snippet", item.get("body", str(item)[:300])))
                                    })
                except Exception:
                    pass

        return results[:limit]
