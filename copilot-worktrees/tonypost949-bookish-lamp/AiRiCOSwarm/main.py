"""AiRiCOSwarm Engine Main Controller."""

import argparse
from AiRiCOSwarm.swarm.orchestrator import ChiefInvestigatorAgent

DEFAULT_BATCH_TARGETS = [
    "Andrew Do",
    "Viet America Society",
    "Mercy House",
    "Casa Aliento",
    "APN Parcels",
    "PPP Loans"
]

def main():
    parser = argparse.ArgumentParser(description="AiRiCOSwarm Forensic Intelligence Engine")
    parser.add_argument("--target", type=str, default="Andrew Do", help="Single target entity or keyword")
    parser.add_argument("--mode", type=str, default="cycle", choices=["cycle", "batch", "report"], help="Execution mode")
    parser.add_argument("--batch", action="store_true", help="Execute full multi-target investigation sweep")
    args = parser.parse_args()

    orchestrator = ChiefInvestigatorAgent()
    if args.batch or args.mode == "batch":
        orchestrator.run_batch_sweep(DEFAULT_BATCH_TARGETS)
    else:
        orchestrator.run_investigation_cycle(args.target)

if __name__ == "__main__":
    main()
