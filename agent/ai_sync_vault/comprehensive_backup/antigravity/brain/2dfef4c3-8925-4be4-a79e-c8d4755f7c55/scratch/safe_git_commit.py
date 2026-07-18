import os
import subprocess
import time

repo_dir = r"c:\Users\HP\OneDrive\Documents\OsintNeoAi"
lock_file = os.path.join(repo_dir, ".git", "index.lock")

def clear_lock():
    if os.path.exists(lock_file):
        try:
            os.remove(lock_file)
            print("Removed index.lock successfully.")
        except Exception as e:
            print(f"Error removing lock file: {e}")

def run_git(cmd):
    for i in range(5):
        clear_lock()
        res = subprocess.run(cmd, cwd=repo_dir, capture_output=True, text=True)
        if "index.lock" in res.stderr or "index.lock" in res.stdout:
            print(f"Lock active, retrying {cmd} ({i+1}/5)...")
            time.sleep(1)
        else:
            print(f"Command {' '.join(cmd)} finished.")
            print(f"STDOUT: {res.stdout}")
            print(f"STDERR: {res.stderr}")
            return res.returncode == 0
    return False

# Step 1: git add .
if run_git(["git", "add", "."]):
    # Step 2: git commit
    if run_git(["git", "commit", "-m", "Consolidate workspace structure: backend core, database, pipelines, archives, and Replit exports"]):
        # Step 3: git push
        run_git(["git", "push", "origin", "main"])
