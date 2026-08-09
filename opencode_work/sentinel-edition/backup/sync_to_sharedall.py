#!/usr/bin/env python3
"""
Sentinel Edition - Sync to SharedAll (Google Drive via rclone)
============================================================
Uploads backup archives to the SharedAll/SentinelBackups folder on Google Drive.
Uses rclone (already configured with gdrive: remote).

Usage:
  python sync_to_sharedall.py                    # Upload latest backup
  python sync_to_sharedall.py --list             # List available backups on Drive
  python sync_to_sharedall.py --download <name>  # Download a specific backup
  python sync_to_sharedall.py --verify           # Verify all local backups match Drive
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

BACKUPS_DIR = Path(__file__).parent.parent / "backups"
RCLONE_REMOTE = "gdrive:Sharedall/SentinelBackups"
CONFIG_PATH = Path(__file__).parent / ".sharedall_config.json"


def rclone_cmd(args):
    cmd = ["rclone"] + args
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return result.stdout.strip(), result.returncode


def save_config():
    config = {
        "method": "rclone",
        "remote": RCLONE_REMOTE,
        "setup_date": datetime.now().isoformat(),
        "setup_by": "sentinel_sync_script",
        "note": "Uses rclone gdrive: remote. No OAuth tokens needed.",
    }
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
    print(f"[OK] Config saved to {CONFIG_PATH}")


def sync_latest_backup():
    backups = sorted(BACKUPS_DIR.glob("sentinel_*.zip"), reverse=True)
    if not backups:
        print("[ERROR] No backup archives found. Run create_backup.py first.")
        return False
    latest = backups[0]
    print(f"[SYNC] Uploading: {latest.name}")
    print(f"[SYNC] To: {RCLONE_REMOTE}/")
    output, rc = rclone_cmd(["copy", str(latest), f"{RCLONE_REMOTE}/", "-v"])
    if rc != 0:
        print(f"[ERROR] rclone copy failed (rc={rc})")
        if output:
            print(output)
        return False
    manifest = latest.parent / f"manifest_{latest.stem.split('_', 2)[-1]}.json"
    if manifest.exists():
        rclone_cmd(["copy", str(manifest), f"{RCLONE_REMOTE}/", "-v"])
    info = {
        "latest_backup": latest.name,
        "size_bytes": latest.stat().st_size,
        "uploaded_at": datetime.now().isoformat(),
        "source": "sentinel-edition",
    }
    info_path = BACKUPS_DIR / "latest_backup_info.json"
    with open(info_path, "w") as f:
        json.dump(info, f, indent=2)
    rclone_cmd(["copy", str(info_path), f"{RCLONE_REMOTE}/", "-v"])
    print(f"[OK] Uploaded: {latest.name}")
    save_config()
    return True


def list_backups_remote():
    print(f"[LIST] Listing {RCLONE_REMOTE}/ ...")
    output, rc = rclone_cmd(["ls", f"{RCLONE_REMOTE}/"])
    if rc != 0:
        print(f"[ERROR] rclone ls failed (rc={rc})")
        return
    if not output:
        print("[INFO] No files found in SharedAll/SentinelBackups.")
        return
    print(f"\n{'Size':>12}  {'Name'}")
    print("-" * 74)
    for line in output.split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) == 2:
            size, name = parts
            fname = name.split("/")[-1] if "/" in name else name
            try:
                size_mb = f"{int(size) / (1024*1024):.2f} MB"
            except (ValueError, TypeError):
                size_mb = size
            print(f"{size_mb:>12}  {fname}")


def download_backup(target):
    print(f"[DOWNLOAD] Searching for: {target}")
    output, rc = rclone_cmd(["ls", f"{RCLONE_REMOTE}/"])
    if rc != 0 or not output:
        print("[ERROR] Could not list remote files.")
        return False
    for line in output.split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            continue
        size, name = parts
        fname = name.split("/")[-1] if "/" in name else name
        if target in fname:
            dest = BACKUPS_DIR / fname
            print(f"[DOWNLOAD] Found: {fname}")
            out, rc2 = rclone_cmd(["copy", f"{RCLONE_REMOTE}/{fname}", str(dest), "-v"])
            if rc2 == 0:
                print(f"[OK] Downloaded to: {dest}")
                return True
            else:
                print(f"[ERROR] Download failed (rc={rc2})")
                return False
    print(f"[ERROR] No backup matching '{target}' found.")
    return False


def verify_local_vs_remote():
    print("[VERIFY] Checking local backups vs Drive...")
    local = set(f.name for f in BACKUPS_DIR.glob("sentinel_*.zip"))
    print(f"  Local: {len(local)} backups")
    output, rc = rclone_cmd(["ls", f"{RCLONE_REMOTE}/"])
    remote = set()
    if rc == 0 and output:
        for line in output.split("\n"):
            line = line.strip()
            if not line:
                continue
            parts = line.split(None, 1)
            if len(parts) == 2:
                size, name = parts
                fname = name.split("/")[-1] if "/" in name else name
                if fname.endswith(".zip"):
                    remote.add(fname)
    print(f"  Remote: {len(remote)} backups")
    missing_remote = local - remote
    missing_local = remote - local
    if missing_remote:
        print(f"\n[UPLOAD] {len(missing_remote)} backups not on Drive:")
        for name in sorted(missing_remote):
            src = BACKUPS_DIR / name
            print(f"  Uploading: {name}")
            rclone_cmd(["copy", str(src), f"{RCLONE_REMOTE}/", "-v"])
    if missing_local:
        print(f"\n[DOWNLOAD] {len(missing_local)} backups not local:")
        for name in sorted(missing_local):
            print(f"  Downloading: {name}")
            rclone_cmd(["copy", f"{RCLONE_REMOTE}/{name}", str(BACKUPS_DIR / name), "-v"])
    if not missing_remote and not missing_local:
        print("[OK] All backups in sync!")
    return len(missing_remote) == 0 and len(missing_local) == 0


def main():
    if "--list" in sys.argv:
        list_backups_remote()
    elif "--download" in sys.argv:
        idx = sys.argv.index("--download")
        if idx + 1 < len(sys.argv):
            download_backup(sys.argv[idx + 1])
        else:
            print("Usage: python sync_to_sharedall.py --download <filename>")
    elif "--verify" in sys.argv:
        verify_local_vs_remote()
    else:
        sync_latest_backup()


if __name__ == "__main__":
    main()
