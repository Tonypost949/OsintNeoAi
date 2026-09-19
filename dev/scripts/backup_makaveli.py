import os
import shutil
import datetime
import subprocess

def run_backups():
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    local_paths = [
        r"C:\Users\Amd949609\OneDrive\Documents\OsintNeoAi\backups\repo",
        r"C:\Users\HP\OneDrive\Documents\OsintNeoAi\backups\repo"
    ]
    
    src_makavelli = r"C:\OSINTNEOAI\makavelli"
    src_makaveli = r"C:\OSINTNEOAI\makaveli"
    
    # 1. Local backup
    for lp in local_paths:
        if os.path.exists(lp):
            dest_dir = os.path.join(lp, f"makavelli_{ts}")
            shutil.copytree(src_makavelli, dest_dir, dirs_exist_ok=True)
            print(f"[SUCCESS] Backed up locally to: {dest_dir}")
        else:
            print(f"[INFO] Path not found, skipping: {lp}")
            
    # 2. rclone Google Drive backup
    print("[INFO] Syncing to Sharedall Google Drive via rclone...")
    try:
        cmd1 = ["rclone", "copy", src_makavelli, "gdrive:Sharedall/OsintNeoAi/makavelli/"]
        res1 = subprocess.run(cmd1, capture_output=True, text=True)
        print(f"[RCLONE makavelli] Code: {res1.returncode}, Out: {res1.stdout}, Err: {res1.stderr}")
        
        cmd2 = ["rclone", "copy", src_makaveli, "gdrive:Sharedall/OsintNeoAi/makaveli/"]
        res2 = subprocess.run(cmd2, capture_output=True, text=True)
        print(f"[RCLONE makaveli] Code: {res2.returncode}, Out: {res2.stdout}, Err: {res2.stderr}")
    except Exception as e:
        print(f"[ERROR] rclone error: {e}")
        
    print("[SUCCESS] Backup process completed.")

if __name__ == "__main__":
    run_backups()
