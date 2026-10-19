#!/usr/bin/env python3
"""
extract_and_upload.py — Gemini Takeout Filter & Rclone Synchronization Engine
Extracts specific Gemini chat sessions and NotebookLM references from a Google Takeout dump
and synchronizes clean exports to Google Drive and local master indexes.
"""

import os
import sys
import json
import shutil
import subprocess
import argparse
from pathlib import Path

DEFAULT_TAKEOUT_DIR = r"C:\OsintNeoAi\data\chats\Takeout"
DEFAULT_REGISTRY_FILE = r"C:\OsintNeoAi\data\gemini_session_links_registry.json"
DEFAULT_OUTPUT_DIR = r"C:\OsintNeoAi\data\filtered_chats"
DEFAULT_RCLONE_DESTINATION = "gdrive:Sharedall/Gemini_Exports"


def load_target_registry(registry_path):
    """Extracts session IDs and notebook IDs from the registry JSON."""
    session_ids = set()
    notebook_ids = set()
    if not os.path.exists(registry_path):
        print(f"[!] Registry file not found at: {registry_path}")
        return session_ids, notebook_ids

    try:
        with open(registry_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Parse gemini_chat_sessions / chat_sessions
        chat_items = data.get("gemini_chat_sessions", []) or data.get("chat_sessions", [])
        for item in chat_items:
            if isinstance(item, dict):
                sid = item.get("session_id")
                url = item.get("url", "")
                if sid:
                    session_ids.add(sid)
                elif "gemini.google.com/app/" in url:
                    session_ids.add(url.split("/")[-1].split("?")[0])
            elif isinstance(item, str):
                session_ids.add(item)

        # Parse notebooks
        notebook_items = data.get("notebooks", [])
        for item in notebook_items:
            if isinstance(item, dict):
                nid = item.get("id")
                if nid:
                    notebook_ids.add(nid)

        print(f"[+] Loaded {len(session_ids)} chat session IDs and {len(notebook_ids)} notebook IDs from registry.")
    except Exception as e:
        print(f"[!] Error parsing registry file: {e}")

    return session_ids, notebook_ids


def scan_and_filter_takeout(takeout_path, session_ids, notebook_ids, output_dir):
    """Scans the Takeout folder matching filename AND deep contents for session IDs."""
    takeout_path = Path(takeout_path)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    if not takeout_path.exists():
        print(f"[!] Takeout directory does not exist: {takeout_path}")
        print(f"[*] Please extract your Google Takeout zip file into: {takeout_path}")
        return 0

    all_targets = session_ids.union(notebook_ids)
    matched_count = 0
    scanned_files = 0

    print(f"[*] Scanning {takeout_path} for {len(all_targets)} target identifiers...")

    for root, _, files in os.walk(takeout_path):
        for fname in files:
            scanned_files += 1
            fpath = os.path.join(root, fname)
            is_match = False
            matched_id = None

            # 1. Quick check: filename contains target ID
            for tid in all_targets:
                if tid in fname:
                    is_match = True
                    matched_id = tid
                    break

            # 2. Deep check: inspect file contents if it's text/html/json
            if not is_match and fname.lower().endswith((".json", ".html", ".htm", ".txt", ".csv")):
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as tf:
                        content_sample = tf.read(500000) # Check first 500KB
                        for tid in all_targets:
                            if tid in content_sample:
                                is_match = True
                                matched_id = tid
                                break
                except Exception:
                    pass

            if is_match:
                matched_count += 1
                dest_fname = f"filtered_{matched_id}_{fname}" if matched_id not in fname else fname
                dest_file = output_path / dest_fname
                try:
                    shutil.copy2(fpath, dest_file)
                    print(f"  [✓] Matched ({matched_id}): {fname} -> {dest_file.name}")
                except Exception as e:
                    print(f"  [!] Failed to copy {fname}: {e}")

    print(f"[+] Scan complete: Scanned {scanned_files} files, matched {matched_count} target sessions.")
    return matched_count


def upload_to_drive(local_dir, rclone_dest):
    """Synchronizes the filtered folder to Google Drive via rclone."""
    print(f"[*] Synchronizing {local_dir} to {rclone_dest} via rclone...")
    try:
        cmd = ["rclone", "copy", str(local_dir), str(rclone_dest), "--progress"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("[+] Rclone synchronization successful!")
        if result.stdout:
            print(result.stdout)
    except FileNotFoundError:
        print("[!] 'rclone' executable not found on PATH. Files remain safely preserved locally.")
    except subprocess.CalledProcessError as e:
        print(f"[!] Rclone error (Exit Code {e.returncode}): {e.stderr}")


def main():
    parser = argparse.ArgumentParser(description="Filter Takeout Gemini chats and sync to Google Drive.")
    parser.add_argument("--takeout-dir", default=DEFAULT_TAKEOUT_DIR, help="Path to extracted Takeout directory")
    parser.add_argument("--registry", default=DEFAULT_REGISTRY_FILE, help="Path to session registry JSON")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="Local output directory for matches")
    parser.add_argument("--rclone-dest", default=DEFAULT_RCLONE_DESTINATION, help="Remote rclone target path")
    parser.add_argument("--no-upload", action="store_true", help="Skip rclone upload step")
    args = parser.parse_args()

    print("=" * 60)
    print("  GEMINI TAKEOUT TARGET EXTRACTOR & RCLONE SYNC")
    print("=" * 60)

    session_ids, notebook_ids = load_target_registry(args.registry)
    if not session_ids and not notebook_ids:
        print("[!] No target IDs found in registry. Exiting.")
        sys.exit(1)

    matched = scan_and_filter_takeout(args.takeout_dir, session_ids, notebook_ids, args.output_dir)

    if matched > 0 and not args.no_upload:
        upload_to_drive(args.output_dir, args.rclone_dest)
    elif matched == 0:
        print(f"[*] Note: If you haven't extracted your Takeout zip yet, extract it to:\n    {args.takeout_dir}")
        print(f"[*] Then rerun this script to automatically extract and upload the filtered sessions.")

if __name__ == "__main__":
    main()
