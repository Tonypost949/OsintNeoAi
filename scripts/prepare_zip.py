#!/usr/bin/env python3
import os
import zipfile
import datetime
import shutil

PROJECT_ROOT = r"C:\OsintNeoAi"
DIST_DIR = os.path.join(PROJECT_ROOT, "dist")
os.makedirs(DIST_DIR, exist_ok=True)

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
zip_name = f"OsintNeoAi_{timestamp}.zip"
zip_latest = "OsintNeoAi_latest.zip"
zip_path = os.path.join(DIST_DIR, zip_name)
latest_path = os.path.join(DIST_DIR, zip_latest)

ROOT_FILES = [
    "package.json", "manifest.json", "README.md", "requirements.txt",
    "index.html", "server.py", "app.py", "AGENTS.md"
]

print("=" * 60)
print("       Packaging OsintNeoAi Distribution Archive        ")
print("=" * 60)
print(f"Project Root : {PROJECT_ROOT}")
print(f"Output Target: {zip_path}")

file_count = 0
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
    # Add root files
    for filename in ROOT_FILES:
        fp = os.path.join(PROJECT_ROOT, filename)
        if os.path.isfile(fp):
            zipf.write(fp, filename)
            file_count += 1
            
    # Add scripts folder
    scripts_dir = os.path.join(PROJECT_ROOT, "scripts")
    if os.path.isdir(scripts_dir):
        for f in os.listdir(scripts_dir):
            full_fp = os.path.join(scripts_dir, f)
            if os.path.isfile(full_fp) and not f.endswith((".pyc", ".tmp", ".log")):
                rel_fp = os.path.relpath(full_fp, PROJECT_ROOT)
                zipf.write(full_fp, rel_fp)
                file_count += 1

    # Add public folder
    public_dir = os.path.join(PROJECT_ROOT, "public")
    if os.path.isdir(public_dir):
        for root, dirs, files in os.walk(public_dir):
            for f in files:
                full_fp = os.path.join(root, f)
                rel_fp = os.path.relpath(full_fp, PROJECT_ROOT)
                zipf.write(full_fp, rel_fp)
                file_count += 1

shutil.copy2(zip_path, latest_path)

print(f"[+] Total files archived : {file_count}")
print(f"[+] Timestamped Package  : {zip_path}")
print(f"[+] Latest Package       : {latest_path}")
print("=" * 60)
