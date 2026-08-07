#!/usr/bin/env python3
"""
Sentinel Edition - Verify Backups
==================================
Checks all backup locations and reports status.

Usage: python verify_backups.py
"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SENTINEL_DIR = Path(__file__).resolve().parent.parent
BACKUPS_DIR = SENTINEL_DIR / "backups"

LOCAL_BACKUP_DIRS = [
    Path(r"C:\Users\HP\OneDrive\Documents\github_backups"),
    Path(r"C:\Users\HP\OneDrive\Documents\opencode_work_backup"),
    Path(r"C:\Users\HP\OneDrive\Documents\OsintNeoAi_backup"),
    Path(r"C:\Users\HP\sentinel_backups"),
]

SHAREDALL_CONFIG = SENTINEL_DIR / "backup" / ".sharedall_config.json"


def file_hash(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def check_git_status():
    """Check git repo status."""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=10
        )
        uncommitted = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0

        result2 = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=10
        )
        last_commit = result2.stdout.strip()

        result3 = subprocess.run(
            ["git", "remote", "-v"],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=10
        )
        remote = result3.stdout.strip().split("\n")[0] if result3.stdout else "none"

        return {
            "status": "ok",
            "uncommitted_changes": uncommitted,
            "last_commit": last_commit,
            "remote": remote,
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def check_local_backups():
    """Check all local backup directories."""
    results = []
    for backup_dir in LOCAL_BACKUP_DIRS:
        if not backup_dir.exists():
            results.append({
                "path": str(backup_dir),
                "exists": False,
                "backups": 0,
                "latest": None,
            })
            continue

        backups = sorted(backup_dir.glob("sentinel_*.zip"), reverse=True)
        latest = None
        if backups:
            latest = {
                "name": backups[0].name,
                "size_mb": backups[0].stat().st_size / (1024 * 1024),
                "modified": datetime.fromtimestamp(backups[0].stat().st_mtime).isoformat(),
                "hash": file_hash(backups[0]),
            }

        results.append({
            "path": str(backup_dir),
            "exists": True,
            "backups": len(backups),
            "latest": latest,
        })
    return results


def check_sentinel_workspace():
    """Check the sentinel-edition workspace."""
    critical_files = [
        "core/engine.py",
        "collectors/web_collector.py",
        "collectors/public_records.py",
        "analyzers/text_analyzer.py",
        "analyzers/network_analyzer.py",
        "exports/html_report.py",
        "exports/geojson_export.py",
        "cli.py",
        "README.md",
        "BACKUP_PROTOCOL.md",
        "requirements.txt",
        "tests/test_engine.py",
    ]

    results = []
    for f in critical_files:
        path = SENTINEL_DIR / f
        results.append({
            "file": f,
            "exists": path.exists(),
            "size": path.stat().st_size if path.exists() else 0,
        })
    return results


def check_sharedall_config():
    """Check SharedAll configuration."""
    if SHAREDALL_CONFIG.exists():
        with open(SHAREDALL_CONFIG) as f:
            config = json.load(f)
        return {
            "configured": True,
            "folder_id": config.get("folder_id", "unknown"),
            "setup_date": config.get("setup_date", "unknown"),
        }
    return {"configured": False}


def main():
    print("=" * 70)
    print("SENTINEL BACKUP VERIFICATION REPORT")
    print(f"Generated: {datetime.utcnow().isoformat()}")
    print("=" * 70)

    # Git status
    print("\n--- GIT STATUS ---")
    git = check_git_status()
    if git["status"] == "ok":
        print(f"  Uncommitted changes: {git['uncommitted_changes']}")
        print(f"  Last commit: {git['last_commit']}")
        print(f"  Remote: {git['remote']}")
        if git["uncommitted_changes"] > 0:
            print("  WARNING: You have uncommitted changes!")
    else:
        print(f"  ERROR: {git['error']}")

    # Local backups
    print("\n--- LOCAL BACKUP DIRECTORIES ---")
    locals_ = check_local_backups()
    total_backups = 0
    for lb in locals_:
        status = "OK" if lb["exists"] and lb["backups"] > 0 else "MISSING" if not lb["exists"] else "EMPTY"
        print(f"  [{status}] {lb['path']}")
        if lb["latest"]:
            print(f"         Latest: {lb['latest']['name']} ({lb['latest']['size_mb']:.1f} MB)")
            total_backups += lb["backups"]
    print(f"  Total backup archives across all locations: {total_backups}")

    # Sentinel workspace
    print("\n--- SENTINEL EDITION FILES ---")
    files = check_sentinel_workspace()
    missing = [f for f in files if not f["exists"]]
    if missing:
        print(f"  WARNING: {len(missing)} critical files missing:")
        for f in missing:
            print(f"    - {f['file']}")
    else:
        print(f"  All {len(files)} critical files present")

    # SharedAll
    print("\n--- SHAREDALL (GOOGLE DRIVE) ---")
    sharedall = check_sharedall_config()
    if sharedall["configured"]:
        print(f"  Configured: Yes")
        print(f"  Folder ID: {sharedall['folder_id']}")
        print(f"  Setup date: {sharedall['setup_date']}")
    else:
        print("  NOT CONFIGURED")
        print("  Run: python sync_to_sharedall.py --setup")

    # Summary
    print("\n" + "=" * 70)
    issues = []
    if git.get("uncommitted_changes", 0) > 0:
        issues.append("Uncommitted changes in git")
    if not sharedall["configured"]:
        issues.append("SharedAll not configured")
    if any(not f["exists"] for f in files):
        issues.append("Missing critical files")
    if total_backups == 0:
        issues.append("No backup archives found anywhere")

    if issues:
        print("ISSUES FOUND:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("ALL CHECKS PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()
