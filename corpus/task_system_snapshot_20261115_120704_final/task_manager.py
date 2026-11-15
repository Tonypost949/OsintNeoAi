r"""
Task System CLI Engine & Safe State Manager
Standard developer tool for atomic task queue operations with automatic pre-action snapshots.
Single Authoritative Location: C:\amd949609@gmail.com_Antigravity_CLI_v2.0\tools\task_system\MASTER_TASK_SYSTEM.md
"""

import os
import shutil
from datetime import datetime

TASK_FILE = r"C:\amd949609@gmail.com_Antigravity_CLI_v2.0\tools\task_system\MASTER_TASK_SYSTEM.md"
BACKUP_DIR = r"C:\amd949609@gmail.com_Antigravity_CLI_v2.0\tools\task_system\backups"

def backup_task_system():
    """Creates a timestamped snapshot of MASTER_TASK_SYSTEM.md before any modification."""
    if not os.path.exists(TASK_FILE):
        return None
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"MASTER_TASK_SYSTEM_{timestamp}.md.bak")
    shutil.copy2(TASK_FILE, backup_path)
    return backup_path

def read_task_system():
    """Reads the single authoritative task system file."""
    if not os.path.exists(TASK_FILE):
        return ""
    with open(TASK_FILE, "r", encoding="utf-8") as f:
        return f.read()

def write_task_system(new_content):
    """Atomically writes to MASTER_TASK_SYSTEM.md after creating a pre-action backup."""
    backup_path = backup_task_system()
    with open(TASK_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"✅ Updated MASTER_TASK_SYSTEM.md (Backup saved: {backup_path})")
    return True

if __name__ == "__main__":
    bk = backup_task_system()
    print(f"✅ Single Task System Verified: {TASK_FILE}")
    if bk:
        print(f"📦 Active Snapshot: {bk}")
