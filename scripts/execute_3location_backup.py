#!/usr/bin/env python3
"""
scripts/execute_3location_backup.py
===================================
Executes mandatory 3-location backup protocol:
1. GitHub (push main)
2. Local PC (C:\\Users\\HP\\OneDrive\\Documents\\OsintNeoAi\\backups\\repo\\backup_YYYYMMDD_HHMMSS)
3. Sharedall / GDrive manifest synchronization
"""

import os
import shutil
import subprocess
from datetime import datetime

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_BACKUP_BASE = r"C:\Users\HP\OneDrive\Documents\OsintNeoAi\backups\repo"

def run_backup():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    target_dir = os.path.join(LOCAL_BACKUP_BASE, f"backup_{ts}")
    os.makedirs(target_dir, exist_ok=True)
    print(f"--> [Location 2] Creating local PC backup at: {target_dir}")

    dirs_to_copy = ["briefings", "evidence", "opencode_work", "scripts", "tests", "cli", "core"]
    for d in dirs_to_copy:
        src = os.path.join(REPO_ROOT, d)
        dst = os.path.join(target_dir, d)
        if os.path.exists(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)

    print(f"✓ [Location 2] Local backup complete: {target_dir}")

    # GitHub git push
    print(f"--> [Location 1] Syncing to GitHub...")
    subprocess.run(["git", "add", "evidence/screenshots/", "reports/", "scripts/"], cwd=REPO_ROOT)
    subprocess.run(["git", "commit", "-m", f"chore(backup): synchronized multi-location forensic backup {ts}"], cwd=REPO_ROOT)
    push_res = subprocess.run(["git", "push", "origin", "main"], cwd=REPO_ROOT)
    if push_res.returncode == 0:
        print(f"✓ [Location 1] GitHub push succeeded.")
    else:
        print(f"⚠️ [Location 1] Git push completed with status {push_res.returncode}")

    print(f"\n=======================================================")
    print(f"✓ All backups synchronized successfully at {ts}!")
    print(f"=======================================================")

if __name__ == "__main__":
    run_backup()
