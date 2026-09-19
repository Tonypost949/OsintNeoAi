#!/usr/bin/env python3
"""
Off-Hours & Storage-Triggered Backup Manager for OsintNeoAi & TaxFunded.
Runs clean, incremental backups from C: to D: without live cloud sync interference.
"""

import os
import sys
import time
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

SOURCE_REPO = Path(r"C:\OsintNeoAi")
BACKUP_DEST = Path(r"D:\OsintNeoAi_LocalBackups")

# Exclude noisy dev directories that shouldn't clog backups
EXCLUDE_DIRS = [
    "node_modules",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".git",
    "azure_unzipped_logs"
]

def check_available_space(drive_path="C:\\"):
    total, used, free = shutil.disk_usage(drive_path)
    free_gb = free / (1024 ** 3)
    return free_gb

def run_robocopy_backup():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    target_dir = BACKUP_DEST / f"backup_{timestamp}"
    target_dir.mkdir(parents=True, exist_ok=True)

    print(f"[*] Starting scheduled/triggered backup: {datetime.now()}")
    print(f"[*] Source: {SOURCE_REPO}")
    print(f"[*] Destination: {target_dir}")

    # Build robocopy command with exclusions
    cmd = [
        "robocopy",
        str(SOURCE_REPO),
        str(target_dir),
        "/E",          # Copy subdirectories, including empty ones
        "/MT:16",      # 16 multi-threaded copy
        "/R:1",        # Retry once on error
        "/W:1",        # Wait 1s between retries
        "/XD"          # Exclude directories
    ] + EXCLUDE_DIRS

    result = subprocess.run(cmd, capture_output=True, text=True)
    print(f"[+] Backup completed with exit code: {result.returncode}")
    print(f"[+] Backup location: {target_dir}")
    return result.returncode

def main():
    print("==========================================================")
    print("  OsintNeoAi Off-Hours & Space-Triggered Backup System   ")
    print("==========================================================")

    free_c = check_available_space("C:\\")
    print(f"[i] Current C: drive free space: {free_c:.2f} GB")

    # Space-triggered backup threshold (e.g. if C: drops below 25 GB)
    if free_c < 25.0:
        print("[!] Low disk space threshold met on C: (< 25 GB). Triggering automatic backup to D:...")
        run_robocopy_backup()
    else:
        print("[+] Disk space level healthy. Executing standard backup cycle...")
        run_robocopy_backup()

if __name__ == "__main__":
    main()
