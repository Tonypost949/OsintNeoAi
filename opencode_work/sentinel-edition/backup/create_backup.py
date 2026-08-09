#!/usr/bin/env python3
"""
Sentinel Edition - Create Backup Archive
==========================================
Standalone script to create a timestamped backup archive.

Usage: python create_backup.py [description]
"""

import os
import sys
import zipfile
import hashlib
import json
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SENTINEL_DIR = Path(__file__).resolve().parent.parent
BACKUPS_DIR = SENTINEL_DIR / "backups"

BACKUP_EXCLUDE = {
    "__pycache__", "node_modules", ".git", "venv", "env",
    ".env", "*.pyc", ".DS_Store", "sentinel-workspace",
    "backups",  # Don't include backups in backups
}


def get_timestamp():
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")


def create_archive(description="manual"):
    """Create a ZIP archive of the sentinel-edition."""
    timestamp = get_timestamp()
    desc = "_".join(description.split()[:3])[:40]
    archive_name = f"sentinel_{timestamp}_{desc}.zip"
    archive_path = BACKUPS_DIR / archive_name
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Creating: {archive_name}")

    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
        count = 0
        for root, dirs, files in os.walk(SENTINEL_DIR):
            dirs[:] = [d for d in dirs if d not in BACKUP_EXCLUDE]
            for file in files:
                if any(ex in file for ex in BACKUP_EXCLUDE):
                    continue
                filepath = Path(root) / file
                arcname = filepath.relative_to(SENTINEL_DIR.parent)
                zf.write(filepath, arcname)
                count += 1

        # Also include key root files
        for item in ["README.md", "requirements.txt", ".gitignore"]:
            src = REPO_ROOT / item
            if src.is_file():
                zf.write(src, item)
                count += 1

    size_mb = archive_path.stat().st_size / (1024 * 1024)
    print(f"Created: {archive_path}")
    print(f"Size: {size_mb:.1f} MB, Files: {count}")

    # Create manifest
    manifest = {
        "timestamp": datetime.utcnow().isoformat(),
        "description": description,
        "archive": archive_name,
        "size_bytes": archive_path.stat().st_size,
        "file_count": count,
        "hash": hashlib.sha256(open(archive_path, "rb").read()).hexdigest()[:16],
    }
    manifest_path = BACKUPS_DIR / f"manifest_{timestamp}.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    return archive_path


if __name__ == "__main__":
    desc = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "manual"
    create_archive(desc)
