#!/usr/bin/env python3
"""
Sentinel Edition - Pre-Change Backup Script
============================================
MUST be run BEFORE any changes to the repository.
Creates timestamped archives and syncs to all backup locations.

Usage: python pre_change_backup.py [description_of_changes]
"""

import os
import sys
import shutil
import zipfile
import hashlib
import json
import subprocess
from datetime import datetime
from pathlib import Path

# === CONFIGURATION ===
REPO_ROOT = Path(__file__).resolve().parent.parent.parent  # opencode_work root
SENTINEL_DIR = Path(__file__).resolve().parent.parent       # sentinel-edition

LOCAL_BACKUP_DIRS = [
    Path(r"C:\Users\HP\OneDrive\Documents\github_backups"),
    Path(r"C:\Users\HP\OneDrive\Documents\opencode_work_backup"),
    Path(r"C:\Users\HP\OneDrive\Documents\OsintNeoAi_backup"),
]

SHAREDALL_MARKER = REPO_ROOT / "sentinel-edition" / "backup" / ".sharedall_config.json"

# Directories to always include in backups
BACKUP_INCLUDE = [
    "sentinel-edition",
    "README.md",
    "requirements.txt",
    "main.py",
    "Dockerfile",
    "DEPLOYMENT_GUIDE.md",
    ".env.example",
    ".gitignore",
    ".github",
]

# Directories to always exclude
BACKUP_EXCLUDE = {
    "__pycache__", "node_modules", ".git", "venv", "env",
    ".env", "*.pyc", ".DS_Store", "sentinel-workspace",
}


def get_timestamp():
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")


def get_description(args):
    if args:
        return "_".join(args[:3]).replace(" ", "_")[:50]
    return "manual_backup"


def calculate_file_hash(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def create_archive(output_path, description):
    """Create a ZIP archive of the repository."""
    timestamp = get_timestamp()
    archive_name = f"sentinel_backup_{timestamp}_{description}.zip"
    archive_path = output_path / archive_name

    print(f"[BACKUP] Creating archive: {archive_name}")

    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
        files_added = 0

        # Add sentinel-edition directory
        sentinel_path = SENTINEL_DIR
        for root, dirs, files in os.walk(sentinel_path):
            dirs[:] = [d for d in dirs if d not in BACKUP_EXCLUDE]
            for file in files:
                if any(ex in file for ex in BACKUP_EXCLUDE):
                    continue
                filepath = Path(root) / file
                arcname = filepath.relative_to(REPO_ROOT)
                zf.write(filepath, arcname)
                files_added += 1

        # Add root-level files
        for item in BACKUP_INCLUDE:
            src = REPO_ROOT / item
            if src.is_file():
                zf.write(src, item)
                files_added += 1
            elif src.is_dir():
                for root, dirs, files in os.walk(src):
                    dirs[:] = [d for d in dirs if d not in BACKUP_EXCLUDE]
                    for file in files:
                        filepath = Path(root) / file
                        arcname = filepath.relative_to(REPO_ROOT)
                        zf.write(filepath, arcname)
                        files_added += 1

    size_mb = archive_path.stat().st_size / (1024 * 1024)
    print(f"[BACKUP] Created: {archive_path} ({size_mb:.1f} MB, {files_added} files)")
    return archive_path


def sync_to_local(archive_path):
    """Copy the backup archive to all local backup directories."""
    results = []
    for backup_dir in LOCAL_BACKUP_DIRS:
        try:
            backup_dir.mkdir(parents=True, exist_ok=True)
            dest = backup_dir / archive_path.name
            shutil.copy2(archive_path, dest)
            print(f"[BACKUP] Synced to: {dest}")
            results.append({"path": str(dest), "status": "ok"})
        except Exception as e:
            print(f"[BACKUP] FAILED to sync to {backup_dir}: {e}")
            results.append({"path": str(backup_dir), "status": "error", "error": str(e)})
    return results


def sync_to_git(description):
    """Commit current state to git."""
    try:
        os.chdir(REPO_ROOT)
        subprocess.run(["git", "add", "-A"], check=True, capture_output=True)
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            capture_output=True
        )
        if result.returncode == 0:
            print("[BACKUP] No changes to commit")
            return {"status": "no_changes"}

        commit_msg = f"Sentinel backup: {description} [{get_timestamp()}]"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True, capture_output=True)
        subprocess.run(["git", "push", "origin", "main"], check=True, capture_output=True)
        print(f"[BACKUP] Git committed and pushed: {commit_msg}")
        return {"status": "committed", "message": commit_msg}
    except Exception as e:
        print(f"[BACKUP] Git operation failed: {e}")
        return {"status": "error", "error": str(e)}


def create_manifest(archive_path, local_results, git_result, description):
    """Create a backup manifest with metadata."""
    manifest = {
        "timestamp": datetime.utcnow().isoformat(),
        "description": description,
        "archive": str(archive_path),
        "archive_hash": calculate_file_hash(archive_path),
        "archive_size_bytes": archive_path.stat().st_size,
        "local_syncs": local_results,
        "git_sync": git_result,
        "sentinel_version": "1.0.0",
        "agent": "sentinel_backup_system",
    }

    manifest_path = archive_path.parent / f"manifest_{get_timestamp()}.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"[BACKUP] Manifest: {manifest_path}")
    return manifest


def load_sharedall_config():
    """Load SharedAll configuration if available."""
    if SHAREDALL_MARKER.exists():
        with open(SHAREDALL_MARKER) as f:
            return json.load(f)
    return None


def main():
    description = get_description(sys.argv[1:])
    timestamp = get_timestamp()

    print("=" * 60)
    print(f"SENTINEL PRE-CHANGE BACKUP - {timestamp}")
    print(f"Description: {description}")
    print("=" * 60)

    # Step 1: Create archive
    backup_dir = SENTINEL_DIR / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    archive_path = create_archive(backup_dir, description)

    # Step 2: Sync to local backup directories
    local_results = sync_to_local(archive_path)

    # Step 3: Commit to git
    git_result = sync_to_git(description)

    # Step 4: Create manifest
    manifest = create_manifest(archive_path, local_results, git_result, description)

    # Step 5: Check SharedAll config
    sharedall_config = load_sharedall_config()
    if sharedall_config:
        print(f"[BACKUP] SharedAll config found: {sharedall_config.get('folder_id', 'unknown')}")
        print("[BACKUP] Run sync_to_sharedall.py to upload to Google Drive")
    else:
        print("[BACKUP] No SharedAll config found. Run sync_to_sharedall.py --setup to configure.")

    print("=" * 60)
    print("[BACKUP] PRE-CHANGE BACKUP COMPLETE")
    print(f"[BACKUP] Archive: {archive_path}")
    print(f"[BACKUP] Manifest: {manifest_path}")
    print("=" * 60)

    return manifest


if __name__ == "__main__":
    main()
