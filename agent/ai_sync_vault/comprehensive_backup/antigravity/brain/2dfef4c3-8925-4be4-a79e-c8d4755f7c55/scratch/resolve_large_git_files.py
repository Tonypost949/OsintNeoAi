import os
import subprocess
import time

repo_dir = r"c:\Users\HP\OneDrive\Documents\OsintNeoAi"
lock_file = os.path.join(repo_dir, ".git", "index.lock")

def clear_lock():
    if os.path.exists(lock_file):
        try:
            os.remove(lock_file)
        except:
            pass

def run_git(cmd):
    for i in range(5):
        clear_lock()
        res = subprocess.run(cmd, cwd=repo_dir, capture_output=True, text=True)
        if "index.lock" in res.stderr or "index.lock" in res.stdout:
            time.sleep(1)
        else:
            print(f"Command {' '.join(cmd)} finished.")
            print(f"STDOUT: {res.stdout}")
            print(f"STDERR: {res.stderr}")
            return res.returncode == 0
    return False

# Step 1: soft reset commit
run_git(["git", "reset", "--soft", "HEAD~1"])

# Step 2: append ignore rules to .gitignore
gitignore_path = os.path.join(repo_dir, ".gitignore")
with open(gitignore_path, "a") as f:
    f.write("\n# Ignore credentials and temp files in opencode_work\n")
    f.write("opencode_work/temp/\n")
    f.write("opencode_work/OSINT_VAULT_BACKUP/\n")
    f.write("opencode_work/**/google_creds.json\n")
    f.write("**/token.json.stale\n")
    f.write("**/*creds*.json\n")
    f.write("**/client_secret*.json\n")

# Step 3: git reset to unstage everything (and apply gitignore)
run_git(["git", "reset"])

# Step 4: git add .
run_git(["git", "add", "."])

# Step 5: git commit
if run_git(["git", "commit", "-m", "Consolidate workspace structure: backend core, database, pipelines, archives, and Replit exports"]):
    # Step 6: git push
    run_git(["git", "push", "origin", "main"])
