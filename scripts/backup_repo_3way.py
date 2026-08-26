import os
import sys
import shutil
import datetime
import subprocess

def run_cmd(cmd, cwd=None):
    print(f"--> Running: {cmd}")
    res = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if res.stdout:
        print(res.stdout.strip())
    if res.stderr and res.returncode != 0:
        print(f"STDERR: {res.stderr.strip()}")
    return res.returncode

def main():
    repo_dir = r"C:\OsintNeoAi"
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    local_backup_base = r"C:\Users\HP\OneDrive\Documents\OsintNeoAi\backups\repo"
    local_dest = os.path.join(local_backup_base, f"backup_{timestamp}")
    
    print(f"=== Starting 3-Location Backup Protocol [{timestamp}] ===")
    
    # 1. Local PC Backup (C:\ Drive)
    print(f"\n[1/3] Backing up locally to {local_dest}...")
    os.makedirs(local_dest, exist_ok=True)
    # Using robocopy for fast mirroring excluding .git and node_modules
    robocopy_cmd = f'robocopy "{repo_dir}" "{local_dest}" /E /XD .git node_modules /XF *.pyc /R:1 /W:1 /NP /NDL /NFL'
    subprocess.run(robocopy_cmd, shell=True)
    print(f"✓ Local backup completed at: {local_dest}")
    
    # 2. Sharedall Google Drive (via rclone gdrive:)
    print(f"\n[2/3] Backing up to Sharedall Google Drive (gdrive:Sharedall/OsintNeoAi/)...")
    rclone_cmd = f'rclone copy "{local_dest}" "gdrive:Sharedall/OsintNeoAi/backup_{timestamp}" --fast-list --transfers 8 --checkers 16'
    rc_code = run_cmd(rclone_cmd)
    if rc_code == 0:
        print(f"✓ Google Drive backup completed: Sharedall/OsintNeoAi/backup_{timestamp}")
    else:
        print(f"[!] rclone returned code {rc_code}")

    # 3. GitHub Remote (origin main)
    print(f"\n[3/3] Syncing Git changes...")
    run_cmd("git add -A", cwd=repo_dir)
    run_cmd(f'git commit -m "Auto-backup checkpoint {timestamp}"', cwd=repo_dir)
    git_push = run_cmd("git push origin main", cwd=repo_dir)
    if git_push == 0:
        print(f"✓ GitHub push to main succeeded.")
    else:
        print(f"[!] Git push completed with status code {git_push}")

    print("\n=== 3-Location Backup Protocol Finished Successfully ===")

if __name__ == "__main__":
    main()
