#!/usr/bin/env python3
"""
Light Safeguard Snapshot Manager for OsintNeoAi.
Creates instant micro-snapshots (git stash / local patch tags) before major operations.
Zero disk overhead, instant rollbacks.
"""

import subprocess
import sys
from datetime import datetime

def create_safeguard_snapshot(label="auto"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_name = f"safeguard_{label}_{timestamp}"

    # Use git stash create to generate a commit hash of working state without altering working tree
    cmd = ["git", "stash", "create", f"Safeguard Snapshot: {snapshot_name}"]
    res = subprocess.run(cmd, cwd=r"C:\OsintNeoAi", capture_output=True, text=True)

    stash_hash = res.stdout.strip()
    if stash_hash:
        # Create a light tag pointing to this commit hash
        tag_cmd = ["git", "tag", f"safeguard/{label}_{timestamp}", stash_hash]
        subprocess.run(tag_cmd, cwd=r"C:\OsintNeoAi")
        print(f"[+] Light safeguard snapshot created: safeguard/{label}_{timestamp} (Hash: {stash_hash[:8]})")
    else:
        print("[i] Working directory is clean. No snapshot needed.")

def list_snapshots():
    cmd = ["git", "tag", "-l", "safeguard/*"]
    res = subprocess.run(cmd, cwd=r"C:\OsintNeoAi", capture_output=True, text=True)
    print("Available Safeguard Checkpoints:")
    print(res.stdout or "No safeguard snapshots yet.")

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "create"
    if action == "create":
        create_safeguard_snapshot("step")
    elif action == "list":
        list_snapshots()
