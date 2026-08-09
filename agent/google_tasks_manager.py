"""
google_tasks_manager.py — Google Tasks integration for OSINTNeoAi
================================================================
Manage investigation task lists and tasks via Google Tasks API.
Uses device OAuth flow (same as scan_drive.py / scan_google_photos.py).

Usage:
  python google_tasks_manager.py list-lists
  python google_tasks_manager.py list-tasks <list-name>
  python google_tasks_manager.py create-list <list-name>
  python google_tasks_manager.py add <list-name> "<title>" [--due YYYY-MM-DD] [--notes "<text>"]
  python google_tasks_manager.py complete <list-name> <task-id>
  python google_tasks_manager.py update <list-name> <task-id> --title "<new>" --due YYYY-MM-DD --notes "<new>"
  python google_tasks_manager.py init-investigation

First run opens a browser URL — sign in as amd949609@gmail.com.
"""

import os, sys, argparse, datetime, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import auth_helper

SCOPES = ["https://www.googleapis.com/auth/tasks"]
TOKEN_FILE = "tasks_token.json"
CLIENT_SECRET = "client_secret_tasks.json"
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_service():
    creds = auth_helper.authenticate("Google Tasks", SCOPES, TOKEN_FILE, CLIENT_SECRET)
    from googleapiclient.discovery import build
    return build("tasks", "v1", credentials=creds)


def _resolve_list_id(service, name):
    result = service.tasklists().list(maxResults=100).execute()
    for lst in result.get("items", []):
        if lst["title"] == name:
            return lst["id"]
    print(f"[!] Task list '{name}' not found. Available lists:")
    for lst in result.get("items", []):
        print(f"    - {lst['title']}")
    return None


INVESTIGATION_LISTS = [
    {
        "title": "1-Drive/Photos OAuth",
        "tasks": [
            {"title": "Run python agent/run_forensic_scans.py and authorize Drive", "due": None, "notes": "Visit OAuth URL in browser, sign in as amd949609@gmail.com"},
            {"title": "Run python agent/run_forensic_scans.py and authorize Photos", "due": None, "notes": "Second OAuth flow after Drive completes"},
            {"title": "Verify data landed in national_audits.drive_file_index", "due": None, "notes": "Check BigQuery table has new rows"},
            {"title": "Verify data landed in national_audits.google_photos_index", "due": None, "notes": "Check BigQuery table has new rows"},
        ],
    },
    {
        "title": "2-Billing Consolidation",
        "tasks": [
            {"title": "Disable billing on unused GCP projects", "due": None, "notes": "project-9c94c2fa-3af4-49f1-a7b and others"},
            {"title": "Consolidate billing under james account", "due": None, "notes": "Needs browser access to original billing owner"},
            {"title": "Enable Tasks API on GCP project", "due": None, "notes": "gcloud services enable tasks.googleapis.com --project=project-743aab84-f9a5-4ec7-954"},
        ],
    },
    {
        "title": "3-PDF Evidence Extraction",
        "tasks": [
            {"title": "Compare OneDrive scanned PDFs vs Drive PDFs", "due": None, "notes": "Cross-reference Phase I ESA, nuclearshelterphase1, etc."},
            {"title": "Extract text from unprocessed PDFs in BigQuery", "due": None, "notes": "Run content extraction on onedrive_documents where content IS NULL"},
            {"title": "Map addresses to parcels in Huntington Beach", "due": None, "notes": "17631 Cameron Ln, 17642 Beach Blvd, 7942 Speer Dr, etc."},
        ],
    },
    {
        "title": "4-GitHub & Backup Hygiene",
        "tasks": [
            {"title": "Weekly: zip repo and upload to Sharedall Google Drive", "due": None, "notes": "rclone copy ... gdrive:Sharedall/OsintNeoAi_archive/"},
            {"title": "Weekly: create local C:\\ backup", "due": None, "notes": "Copy to C:\\Users\\HP\\OneDrive\\Documents\\OsintNeoAi\\backups\\repo\\"},
            {"title": "Fix git CRLF warnings in repo", "due": None, "notes": "Configure .gitattributes for LF normalization"},
        ],
    },
    {
        "title": "5-Forensic Cross-Reference",
        "tasks": [
            {"title": "Join drive_documents vs onedrive_documents for dedup analysis", "due": None, "notes": "BQ query: SELECT source, COUNT(*) FROM ... GROUP BY source"},
            {"title": "Run entity extraction on all ingested text", "due": None, "notes": "Use core/AG2OSINTNEOMAXX/ for NLP pipeline"},
            {"title": "Build timeline of all document events", "due": None, "notes": "Cross-reference with forensic_layers.fca_timeline"},
        ],
    },
]


def cmd_list_lists(service, args):
    result = service.tasklists().list(maxResults=100).execute()
    items = result.get("items", [])
    if not items:
        print("No task lists found.")
        return
    print(f"\nTask Lists ({len(items)}):")
    print("-" * 50)
    for lst in items:
        print(f"  {lst['title']}  [{lst['id']}]")
    print()


def cmd_list_tasks(service, args):
    list_id = _resolve_list_id(service, args.list_name)
    if not list_id:
        return
    result = service.tasks().list(tasklist=list_id, showCompleted=True, showHidden=True, maxResults=100).execute()
    items = result.get("items", [])
    if not items:
        print(f"No tasks in '{args.list_name}'.")
        return
    print(f"\nTasks in '{args.list_name}' ({len(items)}):")
    print("-" * 70)
    for t in items:
        status = "[DONE]" if t.get("status") == "completed" else "[PEND]"
        due = f"  Due: {t.get('due','')[:10]}" if t.get("due") else ""
        print(f"  {status} {t['title']}{due}")
        print(f"         ID: {t['id']}")
        if t.get("notes"):
            print(f"         Notes: {t['notes'][:80]}")
    print()


def cmd_create_list(service, args):
    body = {"title": args.name}
    result = service.tasklists().insert(body=body).execute()
    print(f"[OK] Created task list: '{result['title']}' [{result['id']}]")


def cmd_add_task(service, args):
    list_id = _resolve_list_id(service, args.list_name)
    if not list_id:
        return
    body = {"title": args.title}
    if args.due:
        body["due"] = args.due + "T00:00:00.000Z"
    if args.notes:
        body["notes"] = args.notes
    result = service.tasks().insert(tasklist=list_id, body=body).execute()
    print(f"[OK] Added task: '{result['title']}' [{result['id']}]")


def cmd_complete_task(service, args):
    list_id = _resolve_list_id(service, args.list_name)
    if not list_id:
        return
    result = service.tasks().get(tasklist=list_id, task=args.task_id).execute()
    result["status"] = "completed"
    service.tasks().update(tasklist=list_id, task=args.task_id, body=result).execute()
    print(f"[OK] Marked task '{result['title']}' as completed.")


def cmd_update_task(service, args):
    list_id = _resolve_list_id(service, args.list_name)
    if not list_id:
        return
    result = service.tasks().get(tasklist=list_id, task=args.task_id).execute()
    if args.title:
        result["title"] = args.title
    if args.due:
        result["due"] = args.due + "T00:00:00.000Z"
    if args.notes:
        result["notes"] = args.notes
    service.tasks().update(tasklist=list_id, task=args.task_id, body=result).execute()
    print(f"[OK] Updated task '{result['title']}'")


def cmd_init_investigation(service, args):
    for lst_def in INVESTIGATION_LISTS:
        name = lst_def["title"]
        existing = service.tasklists().list(maxResults=100).execute()
        list_id = None
        for lst in existing.get("items", []):
            if lst["title"] == name:
                list_id = lst["id"]
                print(f"[SKIP] List '{name}' already exists.")
                break
        if not list_id:
            lst = service.tasklists().insert(body={"title": name}).execute()
            list_id = lst["id"]
            print(f"[OK] Created list '{name}'")
        for task_def in lst_def["tasks"]:
            body = {"title": task_def["title"]}
            if task_def.get("due"):
                body["due"] = task_def["due"]
            if task_def.get("notes"):
                body["notes"] = task_def["notes"]
            service.tasks().insert(tasklist=list_id, body=body).execute()
        print(f"     Added {len(lst_def['tasks'])} tasks.")
    print("\n[DONE] Investigation workspace initialized in Google Tasks!")
    print("Open https://tasks.google.com or check Gmail sidebar.")


def main():
    parser = argparse.ArgumentParser(description="Google Tasks Manager for OSINTNeoAi")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("list-lists", help="Show all task lists")
    p = sub.add_parser("list-tasks", help="Show tasks in a list")
    p.add_argument("list_name")

    p = sub.add_parser("create-list", help="Create a new task list")
    p.add_argument("name")

    p = sub.add_parser("add", help="Add a task to a list")
    p.add_argument("list_name")
    p.add_argument("title")
    p.add_argument("--due", help="Due date YYYY-MM-DD")
    p.add_argument("--notes", help="Task notes/description")

    p = sub.add_parser("complete", help="Mark a task as done")
    p.add_argument("list_name")
    p.add_argument("task_id")

    p = sub.add_parser("update", help="Update a task's title/due/notes")
    p.add_argument("list_name")
    p.add_argument("task_id")
    p.add_argument("--title")
    p.add_argument("--due")
    p.add_argument("--notes")

    p = sub.add_parser("init-investigation", help="Create full investigation task workspace")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    service = get_service()

    cmds = {
        "list-lists": cmd_list_lists,
        "list-tasks": cmd_list_tasks,
        "create-list": cmd_create_list,
        "add": cmd_add_task,
        "complete": cmd_complete_task,
        "update": cmd_update_task,
        "init-investigation": cmd_init_investigation,
    }

    def _noop(svc, a):
        pass

    cmds.get(args.command, _noop)(service, args)


if __name__ == "__main__":
    main()
