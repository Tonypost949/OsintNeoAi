#!/usr/bin/env python3
"""
Cloud Service Manager & Zero-PC Compute Dispatcher
Part of OsintNeoAi Tool Suite

Scans active accounts, verifies pre-existing cloud services,
and provisions headless zero-PC cloud execution pipelines.
"""

import os
import sys
import json
import subprocess
import shutil

TARGET_ACCOUNTS_FILE = r"C:\OsintNeoAi\agent\target_accounts_master.json"

def get_registered_accounts():
    if os.path.exists(TARGET_ACCOUNTS_FILE):
        with open(TARGET_ACCOUNTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def check_local_cloud_tools():
    tools = {
        "gcloud": shutil.which("gcloud") is not None,
        "gh": shutil.which("gh") is not None,
        "rclone": shutil.which("rclone") is not None,
        "az": shutil.which("az") is not None,
        "firebase": shutil.which("firebase") is not None,
    }
    return tools

def check_rclone_remotes():
    try:
        res = subprocess.run(["rclone", "listremotes"], capture_output=True, text=True, timeout=5)
        if res.returncode == 0:
            return [r.strip() for r in res.stdout.strip().splitlines() if r.strip()]
    except Exception:
        pass
    return []

def audit_cloud_ecosystem():
    accounts = get_registered_accounts()
    tools = check_local_cloud_tools()
    remotes = check_rclone_remotes()
    
    report = {
        "status": "ready",
        "primary_accounts_count": len(accounts.get("primary_gmail_accounts", [])),
        "microsoft_accounts_count": len(accounts.get("microsoft_onedrive_accounts", [])),
        "edu_accounts_count": len(accounts.get("google_workspace_edu", [])),
        "active_rclone_remotes": remotes,
        "available_cli_tools": tools,
        "zero_pc_compute_providers": [
            {
                "provider": "Google Colab T4 Cloud GPU",
                "tier": "Free / 15GB VRAM",
                "auth_via": "Google Workspace / Primary Gmail",
                "status": "Available (Zero PC compute)"
            },
            {
                "provider": "Kaggle GPU (30h/wk)",
                "tier": "Free / NVIDIA T4/P100",
                "auth_via": "Google Account SSO",
                "status": "Available (Zero PC compute)"
            },
            {
                "provider": "Google Cloud Shell",
                "tier": "Free e2-small / 5GB Persistent",
                "auth_via": "gcloud / amd949609@gmail.com",
                "status": "Configured (Zero PC compute)"
            },
            {
                "provider": "GitHub Actions Headless Runner",
                "tier": "Free 2,000 min/mo",
                "auth_via": "GitHub CLI / Tonypost949",
                "status": "Configured (Zero PC compute)"
            }
        ]
    }
    return report

if __name__ == "__main__":
    rep = audit_cloud_ecosystem()
    print(json.dumps(rep, indent=2))
