"""
tasks.py — OSINTNeoAi task manager
====================================
Stores tasks locally in repo (version controlled, backed up to all 3 locations).
Same structure as Google Tasks lists. No API bullshit.

Usage:
  python tasks.py                          # show all lists
  python tasks.py new-list <name>
  python tasks.py add <list> "<title>" [--due YYYY-MM-DD]
  python tasks.py done <list> <task-id>
  python tasks.py ls <list>
  python tasks.py mv <list> <task-id> <target-list>
  python tasks.py note <list> <task-id> "<text>"
  python tasks.py priority <list> <task-id> <high|med|low>
"""

import json, os, sys, argparse
from datetime import datetime

TASK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.json")

DEFAULT_LISTS = {
    "1-DrivePhotos-OAuth": {
        "created": None,
        "tasks": {
            "1": {"title": "Run run_forensic_scans.py — authorize Drive", "status": "pending", "due": None, "priority": "high", "notes": "python agent/run_forensic_scans.py", "created": None},
            "2": {"title": "Run run_forensic_scans.py — authorize Photos", "status": "pending", "due": None, "priority": "high", "notes": "Second OAuth after Drive", "created": None},
            "3": {"title": "Verify data in BQ: national_audits.drive_file_index", "status": "pending", "due": None, "priority": "med", "notes": "", "created": None},
            "4": {"title": "Verify data in BQ: national_audits.google_photos_index", "status": "pending", "due": None, "priority": "med", "notes": "", "created": None},
        },
    },
    "2-Billing-Consolidation": {
        "created": None,
        "tasks": {
            "1": {"title": "Disable billing on unused GCP projects", "status": "pending", "due": None, "priority": "high", "notes": "project-9c94c2fa-3af4-49f1-a7b etc", "created": None},
            "2": {"title": "Consolidate billing under james account", "status": "pending", "due": None, "priority": "high", "notes": "Needs browser", "created": None},
        },
    },
    "3-PDF-Evidence": {
        "created": None,
        "tasks": {
            "1": {"title": "Cross-reference OneDrive PDFs vs Drive PDFs", "status": "pending", "due": None, "priority": "med", "notes": "Phase I ESA, nuclearshelterphase1, etc", "created": None},
            "2": {"title": "Extract text from unprocessed PDFs in BQ", "status": "pending", "due": None, "priority": "med", "notes": "onedrive_documents WHERE content IS NULL", "created": None},
            "3": {"title": "Map addresses to parcels in Huntington Beach", "status": "pending", "due": None, "priority": "med", "notes": "17631 Cameron, 17642 Beach, 7942 Speer", "created": None},
        },
    },
    "4-Backup-Hygiene": {
        "created": None,
        "tasks": {
            "1": {"title": "Weekly: zip repo → Sharedall Google Drive", "status": "pending", "due": None, "priority": "med", "notes": "rclone copy to gdrive:", "created": None},
            "2": {"title": "Weekly: local C:\\ backup", "status": "pending", "due": None, "priority": "med", "notes": "backups/repo/", "created": None},
            "3": {"title": "Fix git CRLF warnings", "status": "pending", "due": None, "priority": "low", "notes": ".gitattributes", "created": None},
        },
    },
    "5-Forensic-CrossRef": {
        "created": None,
        "tasks": {
            "1": {"title": "Join drive_documents vs onedrive_documents for dedup", "status": "pending", "due": None, "priority": "med", "notes": "BQ query", "created": None},
            "2": {"title": "Run entity extraction on all ingested text", "status": "pending", "due": None, "priority": "med", "notes": "NLP pipeline", "created": None},
            "3": {"title": "Build timeline of all document events", "status": "pending", "due": None, "priority": "med", "notes": "Cross-ref with fca_timeline", "created": None},
        },
    },
}


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def load():
    if not os.path.exists(TASK_FILE):
        data = DEFAULT_LISTS.copy()
        ts = now()
        for lst in data.values():
            lst["created"] = ts
            for t in lst["tasks"].values():
                t["created"] = ts
        save(data)
        return data
    with open(TASK_FILE, encoding="utf-8") as f:
        return json.load(f)


def save(data):
    with open(TASK_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _next_id(tasks):
    if not tasks:
        return "1"
    return str(max(int(k) for k in tasks) + 1)


def cmd_show(data, args):
    for name, lst in data.items():
        total = len(lst["tasks"])
        done = sum(1 for t in lst["tasks"].values() if t["status"] == "done")
        print(f"\n  [{name}]  {done}/{total} done")
        for tid, t in sorted(lst["tasks"].items()):
            icon = "[x]" if t["status"] == "done" else "[ ]"
            due = f"  due:{t['due']}" if t.get("due") else ""
            pri = f"  {t['priority']}" if t.get("priority") and t["priority"] != "med" else ""
            print(f"    {icon} #{tid} {t['title']}{due}{pri}")
    print()


def cmd_new_list(data, args):
    name = args.name
    if name in data:
        print(f"[!] List '{name}' already exists.")
        return
    data[name] = {"created": now(), "tasks": {}}
    save(data)
    print(f"[OK] Created list '{name}'")


def cmd_add(data, args):
    name = args.list_name
    if name not in data:
        print(f"[!] List '{name}' not found. Available: {list(data.keys())}")
        return
    tid = _next_id(data[name]["tasks"])
    data[name]["tasks"][tid] = {
        "title": args.title,
        "status": "pending",
        "due": args.due,
        "priority": args.priority or "med",
        "notes": args.notes or "",
        "created": now(),
    }
    save(data)
    print(f"[OK] #{tid} added to '{name}'")


def cmd_done(data, args):
    for name, lst in data.items():
        if args.task_id in lst["tasks"]:
            lst["tasks"][args.task_id]["status"] = "done"
            save(data)
            print(f"[OK] #{args.task_id} done in '{name}'")
            return
    print(f"[!] Task #{args.task_id} not found")


def cmd_ls(data, args):
    name = args.list_name
    if name not in data:
        print(f"[!] List '{name}' not found. Available: {list(data.keys())}")
        return
    lst = data[name]
    print(f"\n  [{name}] ({len(lst['tasks'])} tasks):")
    for tid, t in sorted(lst["tasks"].items()):
        icon = "[x]" if t["status"] == "done" else "[ ]"
        due = f"  due:{t['due']}" if t.get("due") else ""
        pri = f"  [{t['priority']}]" if t.get("priority") else ""
        notes = f"  -- {t['notes']}" if t.get("notes") else ""
        print(f"    {icon} #{tid} {t['title']}{due}{pri}{notes}")
    print()


def cmd_note(data, args):
    for name, lst in data.items():
        if args.task_id in lst["tasks"]:
            lst["tasks"][args.task_id]["notes"] = args.text
            save(data)
            print(f"[OK] Notes updated for #{args.task_id}")
            return
    print(f"[!] Task #{args.task_id} not found")


def cmd_priority(data, args):
    for name, lst in data.items():
        if args.task_id in lst["tasks"]:
            lst["tasks"][args.task_id]["priority"] = args.level
            save(data)
            print(f"[OK] #{args.task_id} priority set to {args.level}")
            return
    print(f"[!] Task #{args.task_id} not found")


def cmd_move(data, args):
    src = args.src_list
    dst = args.dst_list
    tid = args.task_id
    if src not in data:
        print(f"[!] Source list '{src}' not found"); return
    if dst not in data:
        print(f"[!] Target list '{dst}' not found"); return
    if tid not in data[src]["tasks"]:
        print(f"[!] Task #{tid} not found in '{src}'"); return
    task = data[src]["tasks"].pop(tid)
    new_id = _next_id(data[dst]["tasks"])
    data[dst]["tasks"][new_id] = task
    save(data)
    print(f"[OK] Moved #{tid} from '{src}' to '{dst}' as #{new_id}")


def main():
    parser = argparse.ArgumentParser(description="OSINTNeoAi Task Manager")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("show", help="Show all lists and tasks")

    p = sub.add_parser("new-list")
    p.add_argument("name")

    p = sub.add_parser("add")
    p.add_argument("list_name")
    p.add_argument("title")
    p.add_argument("--due")
    p.add_argument("--notes")
    p.add_argument("--priority", choices=["high", "med", "low"])

    p = sub.add_parser("done")
    p.add_argument("task_id")

    p = sub.add_parser("ls")
    p.add_argument("list_name")

    p = sub.add_parser("note")
    p.add_argument("task_id")
    p.add_argument("text")

    p = sub.add_parser("priority")
    p.add_argument("task_id")
    p.add_argument("level", choices=["high", "med", "low"])

    p = sub.add_parser("mv")
    p.add_argument("src_list")
    p.add_argument("task_id")
    p.add_argument("dst_list")

    args = parser.parse_args()
    data = load()

    cmds = {
        "show": cmd_show,
        "new-list": cmd_new_list,
        "add": cmd_add,
        "done": cmd_done,
        "ls": cmd_ls,
        "note": cmd_note,
        "priority": cmd_priority,
        "mv": cmd_move,
    }
    if args.cmd in cmds:
        cmds[args.cmd](data, args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
