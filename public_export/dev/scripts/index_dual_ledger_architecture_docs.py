#!/usr/bin/env python3
"""
TASK-069: Index Core Architecture Documents for Dual-Ledger OSINT Exchange
Indexes and cross-links architectural blueprints for OSINT Coin Ledger A,
Tax-Funded Token Ledger B, UTXO Data Lineage, and Smart Contract Bounty Splits.
"""

import os
import sys
import json
import hashlib
from datetime import datetime, timezone

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(ROOT_DIR, "data", "dual_ledger_architecture_index.json")

CORE_DOCS = [
    {
        "doc_id": "ARCH-001",
        "title": "Dual-Ledger OSINT Exchange Tokenomics Blueprint",
        "path": "workspaces/NWORICO/data/osint_exchange_tokenomics_blueprint.md",
        "ledger_type": "DUAL_LEDGER_A_B",
        "tags": ["Tokenomics", "Staking", "UTXO", "BountySplits"]
    },
    {
        "doc_id": "ARCH-002",
        "title": "OSINT Exchange User Journeys and Relator Flows",
        "path": "workspaces/NWORICO/data/osint_exchange_user_journeys.md",
        "ledger_type": "USER_JOURNEY",
        "tags": ["Relators", "Victims", "Whistleblowers", "FranchisePress"]
    },
    {
        "doc_id": "ARCH-003",
        "title": "Crypto Architecture Core Reference",
        "path": "workspaces/NWORICO/data/crypto_architecture_core_docs.txt",
        "ledger_type": "CORE_CRYPTO",
        "tags": ["SmartContracts", "ERC20Mock", "DualAuditTokenSystem"]
    },
    {
        "doc_id": "ARCH-004",
        "title": "Immutable Eviction Wiki & Citizen Intelligence Workspace",
        "path": "workspace_v2.html",
        "ledger_type": "CITIZEN_WORKSPACE",
        "tags": ["GenesisWiki", "MaltegoGraph", "ToxicPlumeIntercept", "AcrylicHUD"]
    }
]

def run_indexing():
    print("[TASK-069] Indexing Dual-Ledger Architecture Documents...")
    indexed_entries = []

    for doc in CORE_DOCS:
        full_path = os.path.join(ROOT_DIR, doc["path"].replace("/", os.sep))
        file_hash = "UNAVAILABLE"
        file_size = 0
        exists = os.path.exists(full_path)

        if exists:
            try:
                with open(full_path, "rb") as f:
                    content = f.read()
                    file_hash = hashlib.sha256(content).hexdigest()
                    file_size = len(content)
            except Exception as e:
                print(f"Error reading {full_path}: {e}")

        indexed_entries.append({
            "doc_id": doc["doc_id"],
            "title": doc["title"],
            "relative_path": doc["path"],
            "exists": exists,
            "size_bytes": file_size,
            "sha256_hash": file_hash,
            "ledger_type": doc["ledger_type"],
            "domain_tags": doc["tags"]
        })

    payload = {
        "indexed_at": datetime.now(timezone.utc).isoformat(),
        "total_documents": len(indexed_entries),
        "dual_ledger_system": "OSINT_COIN_A_TAXFUNDED_B",
        "documents": indexed_entries
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"[TASK-069] Successfully generated {OUTPUT_FILE} ({len(indexed_entries)} indexed docs).")

if __name__ == "__main__":
    run_indexing()
