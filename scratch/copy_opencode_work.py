import os
import shutil

src_dir = r"C:\Users\HP\OneDrive\Documents\opencode_work"
dest_dir = r"C:\Users\HP\OneDrive\Documents\OsintNeoAi\opencode_work"

if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)

copied_count = 0
for root, dirs, files in os.walk(src_dir):
    # Exclude directories
    dirs[:] = [d for d in dirs if d not in ('.git', 'node_modules', '.venv', 'venv', '__pycache__', '.pytest_cache')]
    
    for f in files:
        # Exclude massive zip files
        if f.endswith('.zip') and os.path.getsize(os.path.join(root, f)) > 10 * 1024 * 1024:
            continue
            
        sp = os.path.join(root, f)
        rel = os.path.relpath(sp, src_dir)
        dp = os.path.join(dest_dir, rel)
        
        os.makedirs(os.path.dirname(dp), exist_ok=True)
        try:
            shutil.copy2(sp, dp)
            copied_count += 1
        except Exception as e:
            pass

print(f"Successfully consolidated {copied_count} files from opencode_work to {dest_dir}.")
