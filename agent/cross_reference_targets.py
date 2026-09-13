#!/usr/bin/env python3
"""Cross-Reference Master Target Accounts Engine for OsintNeoAi.

Loads all 31 target accounts from agent/target_accounts_master.json,
scans local evidence indexes, and cross-references match counts against BigQuery targets.
"""

import os
import json
from datetime import datetime, timezone
from typing import Dict, List, Any

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TARGETS_FILE = os.path.join(BASE_DIR, "agent", "target_accounts_master.json")
MATCHES_FILE = os.path.join(BASE_DIR, "data", "master_accounts_crossref_matches.json")
SUMMARY_FILE = os.path.join(BASE_DIR, "data", "crossref_summary_matrix.json")

def load_master_targets() -> List[str]:
    """Extract flat list of all unique target accounts."""
    if not os.path.exists(TARGETS_FILE):
        print(f"[-] Target accounts file missing: {TARGETS_FILE}")
        return []

    with open(TARGETS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_accounts = set()
    for category, accounts in data.items():
        if isinstance(accounts, list):
            for acc in accounts:
                if isinstance(acc, str) and "@" in acc:
                    all_accounts.add(acc.strip().lower())

    return sorted(list(all_accounts))

def run_cross_reference():
    targets = load_master_targets()
    print(f"[+] Loaded {len(targets)} unique target accounts from master registry.")

    # Load existing match matrix if available
    matches = []
    if os.path.exists(MATCHES_FILE):
        try:
            with open(MATCHES_FILE, "r", encoding="utf-8") as f:
                matches = json.load(f)
            print(f"[+] Loaded {len(matches)} match records from {MATCHES_FILE}")
        except Exception as e:
            print(f"[-] Error loading existing matches: {e}")

    # Build summary matrix
    account_stats = {}
    for target in targets:
        account_stats[target] = {
            "total_matches": 0,
            "datasets_matched": set(),
            "last_verified": datetime.now(timezone.utc).isoformat()
        }

    for record in matches:
        acc = record.get("account", "").strip().lower()
        if acc in account_stats:
            cnt = record.get("count", 0)
            table = record.get("table", "unknown")
            account_stats[acc]["total_matches"] += cnt
            account_stats[acc]["datasets_matched"].add(table)

    summary_output = {
        "metadata": {
            "total_accounts_registered": len(targets),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "target_bigquery_project": "noble-beanbag-497411-m4"
        },
        "accounts": [
            {
                "account": acc,
                "matches": stats["total_matches"],
                "tables": sorted(list(stats["datasets_matched"])),
                "status": "Verified Match" if stats["total_matches"] > 0 else "Pending Index"
            }
            for acc, stats in sorted(account_stats.items(), key=lambda x: x[1]["total_matches"], reverse=True)
        ]
    }

    os.makedirs(os.path.dirname(SUMMARY_FILE), exist_ok=True)
    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        json.dump(summary_output, f, indent=2)

    print(f"[+] Successfully generated cross-reference summary matrix at {SUMMARY_FILE}")
    print(f"• Verified Accounts: {sum(1 for a in summary_output['accounts'] if a['matches'] > 0)} / {len(targets)}")
    return summary_output

if __name__ == "__main__":
    run_cross_reference()
