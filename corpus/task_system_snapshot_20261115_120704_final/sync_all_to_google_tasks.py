#!/usr/bin/env python3
"""
sync_all_to_google_tasks.py — Unified Google Tasks & Local Ledger Sync Engine
=============================================================================
Enforces Universal AI Law 3:
- Google Tasks (https://tasks.google.com/) is the mandatory primary Task Manager.
- Consolidates active, queued, and completed tasks from active_tasks.json and tasks.json.
- Never blocks on interactive prompts (non-interactive safe per Law 13).
- Always creates a pre-edit backup of active_tasks.json per Law 14.
"""

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ACTIVE_TASKS_FILE = os.path.join(BASE_DIR, "active_tasks.json")
PROFILE_TASKS_FILE = r"C:\Amd949609_Antigravity_v1\tasks\tasks.json"
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
MIRROR_OUT = os.path.join(BASE_DIR, "google_tasks_mirror.json")
TOKEN_PATH = os.path.join(BASE_DIR, "tasks_token.json")
BUILD_POWERAPP = r"C:\Amd949609_Antigravity_v1\tools\build_task_powerapp.py"

NEW_OPERATIONAL_TASKS = [
    {
        "task_id": "TASK-LAW3-GOOGLE-TASKS-20261114",
        "category": "Governance_Law_3",
        "priority": "Critical",
        "summary": "Enforce Google Tasks (https://tasks.google.com/) as mandatory primary Task Manager in Law 3 + Zero Outside-Credit Spend clause across AGENTS.md and .agents/AGENTS.md.",
        "scheduled_mode": "immediate_execution",
        "reversible": True,
        "status": "COMPLETED",
        "completed_at": "2026-11-14T21:50:35-08:00",
        "artifacts_path": r"C:\Amd949609_Antigravity_v1\tools\task_system\google_tasks_mirror.json",
    },
    {
        "task_id": "TASK-ORCH-PORTAL-NEWSPAPER-20261114",
        "category": "Investigator_Portal",
        "priority": "Critical",
        "summary": "Deploy OsintNeoAi Investigator Portal & The Tax-Funded Dispatch Broadsheet Newspaper live on http://localhost:8080/ with latest 2026-11-14 forensic dossiers and sync to GitHub.",
        "scheduled_mode": "immediate_execution",
        "reversible": True,
        "status": "COMPLETED",
        "completed_at": "2026-11-14T21:55:00-08:00",
        "artifacts_path": r"C:\Amd949609_Antigravity_v1\web\newspaper_broadsheet_v3.html",
    },
    {
        "task_id": "TASK-RICO-TOP3-SETTLING-PULLS-20261114",
        "category": "Off_Hours_Automation",
        "priority": "High",
        "summary": "Pull official CA/NV Secretary of State officer records and OC Clerk-Recorder PDFs for Top 3 RICO hubs (11770 Warner Ave, 220 Newport Center Dr, 620 Newport Center Dr), Grant Deed #2018000318921, and Jasmine Place Master Deed ($10M).",
        "scheduled_mode": "off_hours",
        "reversible": True,
        "status": "QUEUED",
        "created_at": "2026-11-14T21:50:00-08:00",
    },
    {
        "task_id": "TASK-FREE-VM-MUSE-KEEPALIVE-20261114",
        "category": "Off_Hours_Automation",
        "priority": "High",
        "summary": "Audit zero-spend VMs (Oracle Always Free, Azure Student, GCP e2-micro) per osintneoai_budget_guard.json (enforce_strict_zero_spend: true) and verify Muse bridge connectivity at 100.79.79.27.",
        "scheduled_mode": "off_hours",
        "reversible": True,
        "status": "IN_PROGRESS",
        "created_at": "2026-11-14T21:50:00-08:00",
    },
    {
        "task_id": "TASK-GOOGLE-ONE-FAMILY-PLAN-20261114",
        "category": "Review_Queue",
        "priority": "High",
        "summary": "Ensure Google One AI Pro & Family Group sharing for amd949609@gmail.com includes all 6 registered Google accounts in unified_account_registry.json via Chrome SSO profile.",
        "scheduled_mode": "daily_review",
        "reversible": True,
        "status": "QUEUED",
        "created_at": "2026-11-14T21:50:00-08:00",
    },
]


def win_to_wsl_path(p: str) -> str:
    if os.name != "nt" and len(p) > 2 and p[1:3] == ":\\":
        drive = p[0].lower()
        rest = p[3:].replace("\\", "/")
        return f"/mnt/{drive}/{rest}"
    return p


def load_json(path: str, default: dict) -> dict:
    p = win_to_wsl_path(path)
    if not os.path.exists(p):
        return default
    with open(p, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def save_json(path: str, data: dict) -> None:
    p = win_to_wsl_path(path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def backup_active_tasks(active_path: str) -> str:
    p = win_to_wsl_path(active_path)
    bdir = win_to_wsl_path(BACKUP_DIR)
    os.makedirs(bdir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = os.path.join(bdir, f"active_tasks.json.bak_{ts}")
    if os.path.exists(p):
        shutil.copy2(p, dst)
    return dst


def try_push_google_tasks(tasks_list: list) -> dict:
    token_p = win_to_wsl_path(TOKEN_PATH)
    if not os.path.exists(token_p):
        return {
            "synced_remote": False,
            "reason": "tasks_token.json not yet authorized locally; exported full mirror payload and PowerApp bridge for https://tasks.google.com/",
        }
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build

        scopes = ["https://www.googleapis.com/auth/tasks"]
        creds = Credentials.from_authorized_user_file(token_p, scopes)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_p, "w", encoding="utf-8") as f:
                f.write(creds.to_json())
        if not creds or not creds.valid:
            return {"synced_remote": False, "reason": "tasks_token.json invalid or expired without refresh token"}

        service = build("tasks", "v1", credentials=creds)
        lists_resp = service.tasklists().list(maxResults=100).execute()
        target_title = "OsintNeoAi Live Operations"
        list_id = None
        for lst in lists_resp.get("items", []):
            if lst.get("title") == target_title:
                list_id = lst.get("id")
                break
        if not list_id:
            created = service.tasklists().insert(body={"title": target_title}).execute()
            list_id = created["id"]

        existing_resp = service.tasks().list(tasklist=list_id, showCompleted=True, showHidden=True, maxResults=100).execute()
        existing_by_title = {t.get("title", ""): t for t in existing_resp.get("items", [])}

        pushed = 0
        for t in tasks_list:
            title = f"[{t.get('task_id')}] {t.get('summary', '')[:120]}"
            status_val = "completed" if str(t.get("status", "")).upper() == "COMPLETED" else "needsAction"
            notes = f"Category: {t.get('category')} | Priority: {t.get('priority')} | Mode: {t.get('scheduled_mode')} | Status: {t.get('status')}"
            if title in existing_by_title:
                ex = existing_by_title[title]
                if ex.get("status") != status_val:
                    ex["status"] = status_val
                    ex["notes"] = notes
                    service.tasks().update(tasklist=list_id, task=ex["id"], body=ex).execute()
                    pushed += 1
            else:
                service.tasks().insert(
                    tasklist=list_id,
                    body={"title": title, "notes": notes, "status": status_val},
                ).execute()
                pushed += 1

        return {"synced_remote": True, "tasklist": target_title, "pushed_or_updated": pushed}
    except Exception as exc:
        return {"synced_remote": False, "reason": f"Google Tasks API push skipped: {exc}"}


def main() -> int:
    bk = backup_active_tasks(ACTIVE_TASKS_FILE)
    active_data = load_json(ACTIVE_TASKS_FILE, {"active_tasks": []})
    bucket = active_data.setdefault("active_tasks", [])
    existing_ids = {t.get("task_id") or t.get("id") for t in bucket}

    added = 0
    for item in NEW_OPERATIONAL_TASKS:
        tid = item["task_id"]
        if tid not in existing_ids:
            bucket.insert(0, item)
            existing_ids.add(tid)
            added += 1

    active_data["last_google_tasks_sync"] = datetime.now().isoformat()
    active_data["primary_task_manager"] = "https://tasks.google.com/"
    save_json(ACTIVE_TASKS_FILE, active_data)

    profile_data = load_json(PROFILE_TASKS_FILE, {"active_and_queued_tasks": [], "completed_tasks": []})
    merged = list(bucket)
    for t in profile_data.get("active_and_queued_tasks", []):
        tid = t.get("task_id") or t.get("id")
        if tid not in existing_ids:
            merged.append(t)
            existing_ids.add(tid)

    api_status = try_push_google_tasks(merged)
    mirror = {
        "generated_at": datetime.now().isoformat(),
        "primary_task_manager": "https://tasks.google.com/",
        "total_tasks": len(merged),
        "newly_added_to_active": added,
        "backup_snapshot": bk,
        "google_tasks_api_sync": api_status,
        "tasks": merged,
    }
    save_json(MIRROR_OUT, mirror)

    powerapp_builder = win_to_wsl_path(BUILD_POWERAPP)
    if os.path.exists(powerapp_builder):
        try:
            subprocess.run([sys.executable, powerapp_builder], check=False, timeout=30)
        except Exception as exc:
            print(f"[!] build_task_powerapp warning: {exc}")

    print(json.dumps({
        "total_tasks": len(merged),
        "added": added,
        "backup": bk,
        "mirror_path": win_to_wsl_path(MIRROR_OUT),
        "google_tasks_api_sync": api_status,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
