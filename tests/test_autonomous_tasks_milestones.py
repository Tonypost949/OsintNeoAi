import os
import sys
import json
import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

def test_task_069_dual_ledger_index():
    index_file = os.path.join(ROOT_DIR, "data", "dual_ledger_architecture_index.json")
    assert os.path.exists(index_file), "dual_ledger_architecture_index.json must exist"
    with open(index_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data.get("total_documents", 0) >= 4
    assert data.get("dual_ledger_system") == "OSINT_COIN_A_TAXFUNDED_B"

def test_task_070_autonomous_suggestive_worker():
    log_file = os.path.join(ROOT_DIR, "data", "autonomous_worker_runs.jsonl")
    assert os.path.exists(log_file), "autonomous_worker_runs.jsonl must exist"
    with open(log_file, "r", encoding="utf-8") as f:
        lines = [json.loads(line) for line in f if line.strip()]
    assert len(lines) > 0

def test_task_072_nworico_graph_scrub():
    report_file = os.path.join(ROOT_DIR, "data", "nworico_daily_graph_scrub_report.json")
    assert os.path.exists(report_file), "nworico_daily_graph_scrub_report.json must exist"
    with open(report_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data.get("graph_health") == "OPTIMAL"

def test_task_074_legal_precedent_extraction():
    legal_index = os.path.join(ROOT_DIR, "data", "legal_precedents_and_statutes_index.json")
    assert os.path.exists(legal_index), "legal_precedents_and_statutes_index.json must exist"
    with open(legal_index, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data.get("total_files_indexed", 0) > 0

def test_task_076_grant_apis_ingestion():
    grants_file = os.path.join(ROOT_DIR, "data", "taxfunded_grants_ingestion.json")
    assert os.path.exists(grants_file), "taxfunded_grants_ingestion.json must exist"
    with open(grants_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data.get("total_grants_tracked", 0) >= 2
    assert data.get("total_disbursed_usd", 0) > 0

def test_task_078_human_in_the_loop_contestation():
    contestation_file = os.path.join(ROOT_DIR, "data", "contestation_review_tasks.json")
    assert os.path.exists(contestation_file), "contestation_review_tasks.json must exist"
    with open(contestation_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data.get("total_active_contestations", 0) >= 1
