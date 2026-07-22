import os
import shutil

src_dir = r"C:\Users\HP\Downloads\ReplitExport-amd949609"
dest_dir = r"c:\Users\HP\OneDrive\Documents\OsintNeoAi\archive\OsintNeoAiReplit"

if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)

copied_count = 0
for item in os.listdir(src_dir):
    sp = os.path.join(src_dir, item)
    dp = os.path.join(dest_dir, item)
    
    if os.path.isdir(sp):
        try:
            if os.path.exists(dp):
                shutil.rmtree(dp)
            shutil.copytree(sp, dp)
            print(f"Copied folder: {item}")
            copied_count += 1
        except Exception as e:
            print(f"Error copying {item}: {e}")
            
print(f"Consolidated {copied_count} folders from ReplitExport to {dest_dir}.")
