#!/usr/bin/env python3
"""
Sentinel Edition - Download from SharedAll
===========================================
Downloads the latest (or specific) backup from SharedAll.

Usage:
  python download_from_sharedall.py              # Download latest
  python download_from_sharedall.py <filename>   # Download specific
"""

import os
import sys
import json
from pathlib import Path

# Import the sharedall sync module
sys.path.insert(0, str(Path(__file__).parent))
from sync_to_sharedall import load_config, get_access_token, list_files_in_folder, download_file

BACKUPS_DIR = Path(__file__).parent.parent / "backups"


def download_latest():
    """Download the latest backup from SharedAll."""
    config = load_config()
    if not config.get("folder_id"):
        print("[ERROR] SharedAll not configured. Run: python sync_to_sharedall.py --setup")
        return False

    access_token = get_access_token(config)
    if not access_token:
        return False

    files = list_files_in_folder(access_token, config["folder_id"])
    if not files:
        print("[INFO] No backups found in SharedAll.")
        return False

    # Find latest zip
    zips = [f for f in files if f["name"].endswith(".zip")]
    if not zips:
        print("[INFO] No ZIP archives found in SharedAll.")
        return False

    latest = zips[0]  # Already sorted by modifiedTime desc
    print(f"[DOWNLOAD] Latest backup: {latest['name']}")

    output = BACKUPS_DIR / latest["name"]
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)

    success = download_file(access_token, latest["id"], output)
    if success:
        print(f"[OK] Downloaded to: {output}")
        # Also download corresponding manifest
        manifest_name = latest["name"].replace("sentinel_backup_", "manifest_").replace(".zip", ".json")
        for f in files:
            if f["name"] == manifest_name:
                download_file(access_token, f["id"], BACKUPS_DIR / manifest_name)
                break
    return success


def download_by_name(name):
    """Download a specific backup by name or hash."""
    config = load_config()
    if not config.get("folder_id"):
        print("[ERROR] SharedAll not configured.")
        return False

    access_token = get_access_token(config)
    if not access_token:
        return False

    files = list_files_in_folder(access_token, config["folder_id"])
    for f in files:
        if name in f["name"]:
            print(f"[DOWNLOAD] Found: {f['name']}")
            output = BACKUPS_DIR / f["name"]
            BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
            return download_file(access_token, f["id"], output)

    print(f"[ERROR] No backup matching '{name}' found.")
    return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        download_by_name(sys.argv[1])
    else:
        download_latest()
