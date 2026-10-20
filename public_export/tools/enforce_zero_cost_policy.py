#!/usr/bin/env python3
"""
Zero-Real-Money & Always-Free Tier Enforcement Policy Tool
Ensures that all AI agents, API calls, BigQuery jobs, and cloud deployments
STRICTLY use Always-Free quotas and non-expiring/student credits.
NEVER incurs out-of-pocket real money charges.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(r"C:\OsintNeoAi")
POLICY_FILE = WORKSPACE / "data" / "zero_cost_enforcement_policy.json"
TASK_FILE = WORKSPACE / "data" / "task_system_registry.json"

ZERO_COST_RULES = {
    "policy_name": "STRICT_ZERO_REAL_MONEY_POLICY",
    "status": "ENFORCED_PERMANENTLY",
    "updated_at": datetime.now().isoformat(),
    "rules": [
        {
            "id": "RULE-FREE-1",
            "name": "Always-Free Priority",
            "description": "Must exhaust 100% Always-Free tiers before touching any promotional or student credits."
        },
        {
            "id": "RULE-FREE-2",
            "name": "Zero Real Money Policy",
            "description": "NEVER enable paid features or billing resources that can draw from credit cards or generate real bills."
        },
        {
            "id": "RULE-FREE-3",
            "name": "Credit Guardrails",
            "description": "Promotional credits (e.g. $100-$500 Edu grants, $200 DigitalOcean, $100 Azure) may only be used after setup is complete and zero risk of overage exists."
        }
    ],
    "approved_free_services": [
        "Google Cloud Shell (5GB Free Linux VM)",
        "Google AI Studio Gemini API Free Tier (15 RPM / 1M TPM)",
        "BigQuery Always-Free (10 GB storage / 1 TB SQL queries per month)",
        "Oracle Cloud Always-Free ARM VPS (4 vCPU / 24 GB RAM / 200 GB Storage)",
        "Azure for Students ($100 Credit - No Credit Card Required)",
        "DigitalOcean Student Pack ($200 Credit for 12 Months via .edu)",
        "Cloudflare Pages & Workers Free Tier"
    ]
}

def enforce_policy():
    print("[+] Registering Zero-Real-Money Policy Guardrails...")
    POLICY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(POLICY_FILE, "w", encoding="utf-8") as f:
        json.dump(ZERO_COST_RULES, f, indent=2)
    print(f"  [✓] Policy saved to: {POLICY_FILE}")

    # Register in task system registry
    task_entry = {
        "id": "TASK-ZERO-COST-ENFORCED",
        "title": "Strict Zero-Real-Money & Always-Free Tier Enforcement",
        "status": "ACTIVE_ENFORCED",
        "timestamp": datetime.now().isoformat(),
        "policy": "ALWAYS_FREE_ONLY_ZERO_REAL_MONEY"
    }

    if TASK_FILE.exists():
        try:
            with open(TASK_FILE, "r", encoding="utf-8") as f:
                tasks = json.load(f)
            if isinstance(tasks, list):
                tasks.append(task_entry)
                with open(TASK_FILE, "w", encoding="utf-8") as f:
                    json.dump(tasks, f, indent=2)
                print(f"  [✓] Registered in task system: {TASK_FILE}")
        except Exception as e:
            print(f"  [!] Task update note: {e}")

if __name__ == "__main__":
    enforce_policy()
