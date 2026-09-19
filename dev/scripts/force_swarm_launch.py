import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi")))
from AiRiCOSwarm.swarm.orchestrator import ChiefInvestigatorAgent
from AiRiCOSwarm.main import DEFAULT_BATCH_TARGETS

def force_swarm():
    print("========================================================")
    print("  OSINT NEO AI - CLOUD SWARM INITIATION SEQUENCE")
    print("========================================================")
    print("[!] OVERRIDING LOCAL LIMITS. INITIATING SWARM PROTOCOL.")
    
    try:
        orchestrator = ChiefInvestigatorAgent()
        print("[+] Swarm Orchestrator Online.")
        print(f"[+] Launching concurrent batch sweep against {len(DEFAULT_BATCH_TARGETS)} master targets...")
        
        results = orchestrator.run_batch_sweep(DEFAULT_BATCH_TARGETS)
        print("\n[OK] SWARM BATCH COMPLETE")
        print(f"    Raw Hits: {results.get('total_raw_hits', 0)}")
        print(f"    Flagged Hits: {results.get('total_flagged_hits', 0)}")
        print(f"    Targets Processed: {results.get('targets_processed', 0)}")
        
    except Exception as e:
        print(f"\n[CRITICAL FAILURE] Swarm launch aborted: {e}")
        print("Note: If error is 'RESOURCE_EXHAUSTED' (429), the API provider quota is strictly blocking the request.")

if __name__ == "__main__":
    force_swarm()
