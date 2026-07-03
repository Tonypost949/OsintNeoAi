#!/usr/bin/env python3
"""
Sync Backups - Automatically extracts all zip files in github_backups/
and incorporates them into the active workspace.
"""

import os
import zipfile
import shutil
from pathlib import Path
import json
from datetime import datetime

BACKUPS_DIR = Path("github_backups")
EXTRACT_STATUS_FILE = Path(".backup_sync_status.json")

def load_status():
    if EXTRACT_STATUS_FILE.exists():
        try:
            with open(EXTRACT_STATUS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_status(status):
    try:
        with open(EXTRACT_STATUS_FILE, "w") as f:
            json.dump(status, f, indent=2)
    except Exception as e:
        print(f"⚠️ Failed to save sync status: {e}")

def get_zip_modified_time(zip_path):
    return os.path.getmtime(zip_path)

def extract_zip(zip_path, dest_dir):
    print("Syncing backup files...")
    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(dest_dir)
        print(f"[SUCCESS] Successfully extracted {zip_path.name}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to extract {zip_path.name}: {e}")
        return False

def sync_all():
    if not BACKUPS_DIR.exists():
        print(f"[ERROR] Backups directory '{BACKUPS_DIR}' does not exist.")
        return

    status = load_status()
    updated = False

    print("\n" + "="*80)
    print("OSINT BACKUP REPOSITORY SYNCHRONIZER")
    print("="*80)

    # Scan for all zip files
    zip_files = list(BACKUPS_DIR.glob("*.zip"))
    print(f"Scanning for zip backups in '{BACKUPS_DIR}' (Found: {len(zip_files)})")

    for zip_path in zip_files:
        zip_name = zip_path.name
        # Folder name is zip name without extension
        folder_name = zip_path.stem
        dest_dir = Path(folder_name)

        mtime = get_zip_modified_time(zip_path)
        last_sync = status.get(zip_name, 0)

        # Extract if not extracted before or if zip has been updated since last extraction
        if last_sync < mtime or not dest_dir.exists():
            success = extract_zip(zip_path, dest_dir)
            if success:
                status[zip_name] = mtime
                updated = True
        else:
            print(f"Skipping up to date backup: {zip_name}")

    if updated:
        save_status(status)

    print("\n" + "="*80)
    print("[SUCCESS] All backup repositories are synchronized!")
    print("="*80)

if __name__ == "__main__":
    sync_all()
