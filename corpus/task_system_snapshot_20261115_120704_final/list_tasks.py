import json

path = r"C:\Amd949609_Antigravity_v1\tools\task_system\active_tasks.json"
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

tasks = data.get("active_tasks", [])
print(f"TOTAL REGISTERED TASKS: {len(tasks)}\n")
print(f"{'STATUS':<12} | {'PRIORITY':<10} | {'TASK ID':<35} | SUMMARY")
print("-" * 110)
for t in tasks:
    status = t.get("status", "QUEUED")
    priority = t.get("priority", "Normal")
    task_id = t.get("task_id", "")
    summary = t.get("summary", "")
    if len(summary) > 55:
        summary = summary[:52] + "..."
    print(f"{status:<12} | {priority:<10} | {task_id:<35} | {summary}")
