"""ChiefInvestigatorAgent (Makaveli): Multi-Target Swarm Orchestration Engine."""

import os
from typing import List, Dict, Any
from AiRiCOSwarm.connectors.bq_connector import BigQueryConnector
from AiRiCOSwarm.swarm.ingestion_agent import EvidenceIngestionAgent
from AiRiCOSwarm.swarm.correlation_agent import RICOCorrelationAgent
from AiRiCOSwarm.swarm.gis_agent import SpatialGISAgent
from AiRiCOSwarm.swarm.reporting_agent import WhistleblowerReportingAgent

class ChiefInvestigatorAgent:
    def __init__(self):
        print("[SWARM] Initializing AiRiCOSwarm Orchestrator...")
        self.bq = BigQueryConnector()
        self.ingestion = EvidenceIngestionAgent(self.bq)
        self.correlation = RICOCorrelationAgent()
        self.gis = SpatialGISAgent()
        self.reporting = WhistleblowerReportingAgent()

    def run_investigation_cycle(self, target_term: str) -> Dict[str, Any]:
        print(f"\n[SWARM] >>> Starting Investigation Cycle: '{target_term}'")
        hits = self.ingestion.search_evidence(target_term, limit=150)
        
        flagged = []
        for h in hits:
            content = f"{h.get('subject', '')} {h.get('snippet', '')}"
            preds = self.correlation.scan_for_predicates(content)
            if preds:
                flagged.append({
                    "title": h.get("subject", "Evidence Hit"),
                    "sender": h.get("sender", "Unknown"),
                    "description": h.get("snippet", ""),
                    "predicates": preds,
                    "date": h.get("date", "")
                })

        print(f"[SWARM] Ingested {len(hits)} raw records -> {len(flagged)} correlated predicate hits.")
        
        # AI Semantic Reasoning Synthesis
        ai_synthesis = self.correlation.synthesize_findings_with_ai(target_term, flagged)
        dossier = self.reporting.generate_dossier(target_term, flagged, ai_synthesis)
        print(f"[SWARM] Dossier generated: {dossier}")
        
        return {
            "target": target_term,
            "raw_hits": len(hits),
            "flagged_hits": len(flagged),
            "dossier_path": dossier,
            "findings": flagged
        }

    def run_batch_sweep(self, targets: List[str]) -> List[Dict[str, Any]]:
        print(f"\n[SWARM] ========================================================")
        print(f"[SWARM] Launching Batch Investigation Sweep ({len(targets)} Targets)")
        print(f"[SWARM] ========================================================")
        
        summary_results = []
        for target in targets:
            res = self.run_investigation_cycle(target)
            summary_results.append(res)
            
        print(f"\n[SWARM] Batch Sweep Complete. All {len(targets)} dossiers produced.")
        return summary_results
