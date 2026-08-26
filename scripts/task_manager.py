#!/usr/bin/env python3
"""
OSINT Neo AI Autonomous Task & Roadmap Manager
Maintains data/tasks.json and syncs with TASKS.md & web API.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(ROOT_DIR, "data", "tasks.json")
BACKUP_DATA_FILE = os.path.join(ROOT_DIR, "cli", "data", "tasks.json")
TASKS_MD = os.path.join(ROOT_DIR, "TASKS.md")

def load_tasks():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"updated_at": datetime.now(timezone.utc).isoformat(), "total": 0, "tasks": []}

def save_tasks(data):
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    data["total"] = len(data.get("tasks", []))
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(BACKUP_DATA_FILE), exist_ok=True)
    
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    with open(BACKUP_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    sync_markdown(data)

def sync_markdown(data):
    tasks = data.get("tasks", [])
    active = [t for t in tasks if t.get("status") in ["TODO", "IN_PROGRESS"]]
    done = [t for t in tasks if t.get("status") == "DONE"]
    
    priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    active.sort(key=lambda x: priority_order.get(x.get("priority", "MEDIUM"), 2))
    
    lines = [
        "# 📋 OSINT Neo AI — Master Autonomous Task & Action Ledger",
        f"> **System Status:** 🟢 Active & Self-Tracking | **Storage:** [`data/tasks.json`](data/tasks.json) | **Total Tasks:** {len(tasks)} ({len(active)} Open / {len(done)} Done)",
        "",
        "---",
        "",
        "## ⚡ Active In-Progress & High-Priority Tasks",
        "",
        "| ID | Priority | Category | Task Description | Action Link / Ref | Status |",
        "| :--- | :---: | :--- | :--- | :--- | :---: |"
    ]
    
    for t in active:
        p_badge = "🔴 **CRITICAL**" if t.get("priority") == "CRITICAL" else ("🟡 **HIGH**" if t.get("priority") == "HIGH" else "🔵 **MEDIUM**")
        lines.append(f"| **`{t['id']}`** | {p_badge} | {t.get('category', 'General')} | **{t['title']}**<br>{t.get('description', '')} | [{t.get('tags', ['Link'])[0]}]({t.get('action_url', '#')}) | `{t.get('status', 'TODO')}` |")
        
    lines.extend([
        "",
        "---",
        "",
        "## ✅ Completed Milestones & Integrated Subsystems",
        "",
        "| ID | Category | Task Title & Delivered Solution | Milestone Date | Status |",
        "| :--- | :--- | :--- | :---: | :---: |"
    ])
    
    for t in done:
        date_str = t.get('created_at', '')[:10]
        lines.append(f"| **`{t['id']}`** | {t.get('category', 'General')} | **{t['title']}**<br>{t.get('description', '')} | {date_str} | `DONE` |")
        
    lines.extend([
        "",
        "---",
        "",
        "## 🛠️ CLI Task Management",
        "```bash",
        "# List active tasks",
        "python scripts/task_manager.py list",
        "",
        "# Add new task",
        "python scripts/task_manager.py add \"Task Title\" --category \"Grants\" --priority \"HIGH\"",
        "",
        "# Mark complete",
        "python scripts/task_manager.py complete \"TASK-001\"",
        "```",
        ""
    ])
    
    with open(TASKS_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[+] Synced {len(tasks)} tasks to {TASKS_MD}")

def list_tasks():
    data = load_tasks()
    tasks = data.get("tasks", [])
    print(f"\n📋 OSINT Neo AI Task Ledger ({len(tasks)} total):\n" + "="*70)
    for t in tasks:
        st = "✅ DONE" if t.get("status") == "DONE" else ("⚡ " + t.get("status"))
        print(f"[{t['id']}] [{t.get('priority', 'MED'):8}] [{st:11}] {t['title']} ({t.get('category', 'General')})")
    print("="*70 + "\n")

def add_task(title, category="General", priority="MEDIUM", description="", action_url="#", tags=None):
    data = load_tasks()
    tasks = data.get("tasks", [])
    next_num = len(tasks) + 1
    new_id = f"TASK-{next_num:03d}"
    
    new_task = {
        "id": new_id,
        "title": title,
        "category": category,
        "priority": priority.upper(),
        "status": "TODO",
        "description": description or title,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "tags": tags or [category],
        "action_url": action_url
    }
    tasks.append(new_task)
    data["tasks"] = tasks
    save_tasks(data)
    print(f"[+] Successfully added [{new_id}] {title}")

def complete_task(task_id):
    data = load_tasks()
    tasks = data.get("tasks", [])
    found = False
    for t in tasks:
        if t["id"].upper() == task_id.upper():
            t["status"] = "DONE"
            found = True
            print(f"[+] Marked [{t['id']}] as DONE!")
            break
    if not found:
        print(f"[-] Task ID {task_id} not found.")
        return
    data["tasks"] = tasks
    save_tasks(data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OSINT Neo AI Task Manager")
    sub = parser.add_subparsers(dest="cmd")
    
    sub.add_parser("list")
    sub.add_parser("sync")
    
    add_p = sub.add_parser("add")
    add_p.add_argument("title", help="Task title")
    add_p.add_argument("--category", default="General")
    add_p.add_argument("--priority", default="MEDIUM", choices=["CRITICAL", "HIGH", "MEDIUM", "LOW"])
    add_p.add_argument("--description", default="")
    add_p.add_argument("--url", default="#")
    
    comp_p = sub.add_parser("complete")
    comp_p.add_argument("task_id", help="Task ID to mark complete (e.g. TASK-008)")
    
    args = parser.parse_args()
    
    if args.cmd == "list" or not args.cmd:
        list_tasks()
    elif args.cmd == "sync":
        data = load_tasks()
        sync_markdown(data)
    elif args.cmd == "add":
        add_task(args.title, category=args.category, priority=args.priority, description=args.description, action_url=args.url)
    elif args.cmd == "complete":
        complete_task(args.task_id)
