from connectors.gdrive_connector import GDriveConnector
from connectors.gmail_connector import GmailConnector
from connectors.onedrive_connector import OneDriveConnector
from processing.correlation import AegisCorrelationEngine
from graph.schema import GraphSchema
from graph.graph_builder import GraphBuilder
from agent.ai_client import AIClient

class CoreAgent:
    """Consolidated main orchestrator driving continuous ingestion, resolution, and graph exporting."""
    
    def __init__(self):
        print("[CoreAgent] Initializing OSINTNeoAI-Core Orchestrator...")
        self.gdrive = GDriveConnector()
        self.gmail = GmailConnector()
        self.onedrive = OneDriveConnector()
        self.correlation = AegisCorrelationEngine()
        self.graph = GraphBuilder()
        self.ai = AIClient()

    def execute_forensic_cycle(self, search_keyword):
        """Orchestrates an entire end-to-end collection, matching, and mapping cycle."""
        results = {
            "gdrive_files": [],
            "onedrive_files": [],
            "gmail_messages": [],
            "correlations": []
        }
        
        # Step 1: Scan and Ingest multi-channel logs
        print(f"\n[CoreAgent] --- Starting Ingestion Cycle for target: '{search_keyword}' ---")
        try:
            results["onedrive_files"] = self.onedrive.scan()
        except Exception as e:
            print(f"[CoreAgent] OneDrive scan bypass: {e}")
            
        try:
            results["gdrive_files"] = self.gdrive.search_drive(f"name contains '{search_keyword}'")
        except Exception as e:
            print(f"[CoreAgent] GDrive search bypass: {e}")

        # Step 2: Unify local folder scans and matching dockets
        print("\n[CoreAgent] --- Starting Entity Resolution & Correlation ---")
        evidence_files = self.correlation.scan_workspace_for_evidence()
        print(f"[CoreAgent] Discovered {len(evidence_files)} available files in workspace.")
        
        # Step 3: Run AI-assisted entity and relationship extraction
        if self.ai.client and results["gdrive_files"]:
            print("\n[CoreAgent] --- Running AI Semantic Processing ---")
            raw_text = " ".join([f.get("name", "") for f in results["gdrive_files"][:5]])
            ai_extractions = self.ai.extract_entity_relationships(raw_text)
            print(f"[CoreAgent] Semantic extraction results: {ai_extractions[:100]}...")
            
        print("\n[CoreAgent] --- Core OSINT cycle completed successfully. ---")
        return results
