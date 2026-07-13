#!/usr/bin/env python3
"""
Sentinel Edition - Sync to Local Backup Folders
=================================================
Copies the latest backup to all local backup directories.

Usage: python sync_to_local.py [archive_name]
"""

import os
import sys
import shutil
import json
from datetime import datetime
from pathlib import Path

BACKUPS_DIR = Path(__file__).resolve().parent.parent / "backups"

LOCAL_BACKUP_DIRS = [
    Path(r"C:\Users\HP\OneDrive\Documents\github_backups"),
    Path(r"C:\Users\HP\OneDrive\Documents\opencode_work_backup"),
    Path(r"C:\Users\HP\OneDrive\Documents\OsintNeoAi_backup"),
]

# Also back up to a local non-OneDrive location for safety
LOCAL_DIRECT_BACKUP = Path(r"C:\Users\HP\sentinel_backups")


def sync_to_all(archive_name=None):
    """Sync backup archive to all local backup directories."""
    # Find the archive
    if archive_name:
        archive = BACKUPS_DIR / archive_name
        if not archive.exists():
            print(f"[ERROR] Archive not found: {archive}")
            return False
    else:
        backups = sorted(BACKUPS_DIR.glob("sentinel_*.zip"), reverse=True)
        if not backups:
            print("[ERROR] No backup archives found. Run pre_change_backup.py first.")
            return False
        archive = backups[0]

    print(f"[SYNC] Syncing: {archive.name}")
    print(f"[SYNC] Size: {archive.stat().st_size / (1024*1024):.1f} MB")
    print()

    results = []

    # Sync to OneDrive-backed folders
    for backup_dir in LOCAL_BACKUP_DIRS:
        try:
            backup_dir.mkdir(parents=True, exist_ok=True)
            dest = backup_dir / archive.name

            # Don't overwrite if identical
            if dest.exists():
                if dest.stat().st_size == archive.stat().st_size:
                    print(f"[SKIP] {backup_dir.name}: already has this backup")
                    results.append({"dir": str(backup_dir), "status": "skipped"})
                    continue

            shutil.copy2(archive, dest)
            print(f"[OK]   {backup_dir.name}: {dest}")
            results.append({"dir": str(backup_dir), "status": "ok"})

            # Also copy manifest if exists
            manifest = archive.parent / f"manifest_{archive.stem.split('_', 2)[-1]}.json"
            if manifest.exists():
                shutil.copy2(manifest, backup_dir / manifest.name)

        except Exception as e:
            print(f"[FAIL] {backup_dir.name}: {e}")
            results.append({"dir": str(backup_dir), "status": "error", "error": str(e)})

    # Sync to direct local backup (not OneDrive-synced)
    try:
        LOCAL_DIRECT_BACKUP.mkdir(parents=True, exist_ok=True)
        dest = LOCAL_DIRECT_BACKUP / archive.name
        shutil.copy2(archive, dest)
        print(f"[OK]   Direct local: {dest}")
        results.append({"dir": str(LOCAL_DIRECT_BACKUP), "status": "ok"})
    except Exception as e:
        print(f"[FAIL] Direct local: {e}")
        results.append({"dir": str(LOCAL_DIRECT_BACKUP), "status": "error", "error": str(e)})

    # Save sync log
    sync_log = BACKUPS_DIR / "sync_log.json"
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "archive": archive.name,
        "results": results,
    }

    log_data = []
    if sync_log.exists():
        with open(sync_log) as f:
            log_data = json.load(f)
    log_data.append(log_entry)
    with open(sync_log, "w") as f:
        json.dump(log_data, f, indent=2)

    ok_count = sum(1 for r in results if r["status"] == "ok")
    print(f"\n[SYNC] Complete: {ok_count}/{len(results)} locations updated")
    return True


def list_all_backups():
    """List all local backup locations and their contents."""
    print("=" * 60)
    print("LOCAL BACKUP LOCATIONS")
    print("=" * 60)

    all_dirs = LOCAL_BACKUP_DIRS + [LOCAL_DIRECT_BACKUP]
    for backup_dir in all_dirs:
        print(f"\n--- {backup_dir} ---")
        if not backup_dir.exists():
            print("  (directory does not exist)")
            continue
        files = sorted(backup_dir.glob("sentinel_*.zip"), reverse=True)
        if not files:
            print("  (no sentinel backups found)")
            continue
        for f in files[:5]:
            size_mb = f.stat().st_size / (1024 * 1024)
            mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            print(f"  {f.name}  ({size_mb:.1f} MB, {mtime})")
        if len(files) > 5:
            print(f"  ... and {len(files) - 5} more")


def main():
    if "--list" in sys.argv:
        list_all_backups()
    else:
        archive_name = sys.argv[1] if len(sys.argv) > 1 else None
        sync_to_all(archive_name)


if __name__ == "__main__":
    main()
