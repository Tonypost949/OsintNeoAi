import os
import shutil

src_root = r"C:\Users\HP\OneDrive\Imports\txtdjdrop@gmail.com - Google Drive\ERA EDR"
dest_dir = r"C:\Users\HP\OneDrive\Documents\opencode_work\Private_EDR_2025_Real"

# Also check IronMan DaVinci imports
ironman_src = r"C:\Users\HP\OneDrive\Imports"

os.makedirs(dest_dir, exist_ok=True)
copied_count = 0

print("[*] Scanning ALL import folders for 7969270 series real EDR files...")

# Walk ALL import subdirs to find 7969270 files
for root, dirs, files in os.walk(ironman_src):
    for file in files:
        if file.startswith("7969270") or file.startswith("79692706") or file.startswith("79692705") or file.startswith("79692707"):
            src_path = os.path.join(root, file)
            dest_path = os.path.join(dest_dir, file)
            if not os.path.exists(dest_path):
                try:
                    shutil.copy2(src_path, dest_path)
                    print(f"  [+] Copied: {file} ({os.path.getsize(src_path)} bytes)")
                    copied_count += 1
                except Exception as e:
                    print(f"  [ERROR] {file}: {e}")

# Also check Downloads (1) and Downloads
for alt_dir in [r"C:\Users\HP\OneDrive\Downloads (1)", r"C:\Users\HP\Downloads"]:
    if os.path.exists(alt_dir):
        for f in os.listdir(alt_dir):
            if f.startswith("7969270") or f.startswith("79692706") or f.startswith("79692705"):
                src_path = os.path.join(alt_dir, f)
                dest_path = os.path.join(dest_dir, f)
                if not os.path.exists(dest_path):
                    try:
                        shutil.copy2(src_path, dest_path)
                        print(f"  [+] Copied from {alt_dir}: {f}")
                        copied_count += 1
                    except Exception as e:
                        print(f"  [ERROR] {f}: {e}")

print(f"\n[DONE] Total 7969270 series files staged: {copied_count}")
print(f"[INFO] All real EDR files now together in: {dest_dir}")
