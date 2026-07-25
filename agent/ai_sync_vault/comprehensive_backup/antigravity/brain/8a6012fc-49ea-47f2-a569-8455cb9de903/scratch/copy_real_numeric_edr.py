import os
import shutil
import glob

src_root = r"C:\Users\HP\OneDrive\Imports\txtdjdrop@gmail.com - Google Drive\ERA EDR"
dest_dir = r"C:\Users\HP\OneDrive\Documents\opencode_work\Private_EDR_2025_Real"

os.makedirs(dest_dir, exist_ok=True)

print(f"[*] Scanning {src_root} and subfolders for real numeric EDR files (7887036*)...")

copied_count = 0
# Recursively search for any file starting with 7887036
for root, dirs, files in os.walk(src_root):
    for file in files:
        if file.startswith("7887036"):
            src_path = os.path.join(root, file)
            dest_path = os.path.join(dest_dir, file)
            if not os.path.exists(dest_path):
                try:
                    shutil.copy2(src_path, dest_path)
                    print(f"  [+] Copied Real EDR: {file} ({os.path.getsize(src_path)} bytes)")
                    copied_count += 1
                except Exception as e:
                    print(f"  [ERROR] Failed to copy {file}: {e}")

print(f"\n[SUCCESS] Staged all real numeric EDR files! Total copied: {copied_count}")
