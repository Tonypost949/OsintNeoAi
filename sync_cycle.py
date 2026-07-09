#!/usr/bin/env python3
import os
import subprocess
import time
from pathlib import Path

WORKSPACE_DIR = r"c:\Users\HP\OneDrive\Documents\OsintNeoAi"

def run_cmd(cmd, cwd=WORKSPACE_DIR, retries=3, delay=10):
    for attempt in range(retries):
        print(f"Executing (Attempt {attempt + 1}/{retries}): {' '.join(cmd)}")
        try:
            res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True)
            print(f"STDOUT: {res.stdout}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"ERROR on attempt {attempt + 1}: {e.stderr}")
            if attempt < retries - 1:
                print(f"Waiting {delay}s before retrying...")
                time.sleep(delay)
            else:
                return False

def main():
    print("=== STARTING CONTINUOUS SYNC CYCLE ===")
    
    # 1. Run sync_backups.py to extract any newly deposited zips
    run_cmd(["python", "sync_backups.py"])
    
    # 2. Check git status
    try:
        status_res = subprocess.run(["git", "status", "--porcelain"], cwd=WORKSPACE_DIR, capture_output=True, text=True, check=True)
        if status_res.stdout.strip():
            print("Detected unstaged/uncommitted files in Git. Staging and committing...")
            run_cmd(["git", "add", "."])
            run_cmd(["git", "commit", "-m", "Auto-commit: Synchronized workspace changes by OSINT agent"])
            run_cmd(["git", "push", "origin", "main"])
        else:
            print("Git tree clean. No updates to push.")
    except Exception as e:
        print(f"Git check failed: {e}")
        
    # 3. Sync full workspace to Google Drive via rclone
    run_cmd([
        "rclone", "sync", 
        WORKSPACE_DIR, 
        "gdrive:Sharedall/OsintNeoAi",
        "--exclude", "node_modules/**",
        "--exclude", ".git/**",
        "--exclude", "__pycache__/**"
    ], retries=5, delay=15)
    
    # 4. Sync opencode_work folder specifically
    run_cmd([
        "rclone", "sync",
        os.path.join(WORKSPACE_DIR, "opencode_work"),
        "gdrive:Sharedall/opencode_work"
    ], retries=5, delay=15)
    
    print("=== SYNC CYCLE COMPLETED ===")

if __name__ == "__main__":
    main()
