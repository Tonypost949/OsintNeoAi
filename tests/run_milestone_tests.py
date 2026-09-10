import os
import sys
import json

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

def run_all_tests():
    print("=== Running Autonomous Task Milestone Verification Suite ===")
    
    # 1. TASK-069
    index_file = os.path.join(ROOT_DIR, "data", "dual_ledger_architecture_index.json")
    assert os.path.exists(index_file), "dual_ledger_architecture_index.json must exist"
    with open(index_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data.get("total_documents", 0) >= 4, "Must index at least 4 architecture docs"
    assert data.get("dual_ledger_system") == "OSINT_COIN_A_TAXFUNDED_B"
    print("✅ TASK-069: Dual-Ledger Architecture Index Verified")

    # 2. TASK-070
    log_file = os.path.join(ROOT_DIR, "data", "autonomous_worker_runs.jsonl")
    assert os.path.exists(log_file), "autonomous_worker_runs.jsonl must exist"
    with open(log_file, "r", encoding="utf-8") as f:
        lines = [json.loads(line) for line in f if line.strip()]
    assert len(lines) > 0, "Autonomous worker must process queue items"
    print(f"✅ TASK-070: Autonomous Task Worker Verified ({len(lines)} runs logged)")

    # 3. TASK-072
    report_file = os.path.join(ROOT_DIR, "data", "nworico_daily_graph_scrub_report.json")
    assert os.path.exists(report_file), "nworico_daily_graph_scrub_report.json must exist"
    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data.get("graph_health") == "OPTIMAL"
    print("✅ TASK-072: NWORICO Daily Graph Scrub Verified (Health: OPTIMAL)")

    # 4. TASK-074
    legal_index = os.path.join(ROOT_DIR, "data", "legal_precedents_and_statutes_index.json")
    assert os.path.exists(legal_index), "legal_precedents_and_statutes_index.json must exist"
    with open(legal_index, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data.get("total_files_indexed", 0) > 0
    print(f"✅ TASK-074: Legal Precedent & Statute Extraction Verified ({data.get('total_files_indexed')} files)")

    # 5. TASK-076
    grants_file = os.path.join(ROOT_DIR, "data", "taxfunded_grants_ingestion.json")
    assert os.path.exists(grants_file), "taxfunded_grants_ingestion.json must exist"
    with open(grants_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data.get("total_grants_tracked", 0) >= 2
    assert data.get("total_disbursed_usd", 0) > 0
    print(f"✅ TASK-076: Public Grant APIs Ingestion Verified (${data.get('total_disbursed_usd'):,.2f} tracked)")

    # 6. TASK-078
    contestation_file = os.path.join(ROOT_DIR, "data", "contestation_review_tasks.json")
    assert os.path.exists(contestation_file), "contestation_review_tasks.json must exist"
    with open(contestation_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data.get("total_active_contestations", 0) >= 1
    print(f"✅ TASK-078: Human-in-the-Loop Contestation System Verified ({data.get('total_active_contestations')} tickets)")

    print("\n🎉 ALL 6 AUTONOMOUS TASK MILESTONES 100% PASSED!")

if __name__ == "__main__":
    run_all_tests()
