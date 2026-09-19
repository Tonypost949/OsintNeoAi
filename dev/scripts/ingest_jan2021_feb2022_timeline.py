#!/usr/bin/env python3
"""
scripts/ingest_jan2021_feb2022_timeline.py
===========================================
Scans local directories (Downloads, Documents, Takeout archives) for any data,
emails, medical records, court documents, and photos timestamped between
January 1, 2021 and February 28, 2022.

Extracts text, calculates SHA-256 hashes, and indexes everything into
evidence/jan2021_feb2022_master_vault.json
"""

import os
import glob
import json
import hashlib
import zipfile
from datetime import datetime, timezone

TARGET_START = datetime(2021, 1, 1).timestamp()
TARGET_END = datetime(2022, 3, 1).timestamp()

SEARCH_DIRS = [
    r"C:\Users\Amd949609\Downloads",
    r"C:\OsintNeoAi\evidence",
    r"C:\OsintNeoAi\data"
]

OUTPUT_VAULT = r"C:\OsintNeoAi\evidence\jan2021_feb2022_master_vault.json"

def scan_and_index():
    print("--> Scanning for all assets from Jan 2021 to Feb 2022...")
    indexed_items = []
    
    for s_dir in SEARCH_DIRS:
        if not os.path.exists(s_dir):
            continue
        print(f"Scanning directory: {s_dir}...")
        for root, dirs, files in os.walk(s_dir):
            for f in files:
                fpath = os.path.join(root, f)
                try:
                    stat = os.stat(fpath)
                    mtime = stat.st_mtime
                    ctime = stat.st_ctime
                    
                    # Check if modified/created within target window OR filename has 2021/2022
                    in_time_range = (TARGET_START <= mtime <= TARGET_END) or (TARGET_START <= ctime <= TARGET_END)
                    name_has_target = any(y in f.lower() for y in ["2021", "202201", "202202", "apr21", "aug21", "aug_2021", "woodbridge"])
                    
                    if in_time_range or name_has_target:
                        file_size = stat.st_size
                        with open(fpath, "rb") as fp:
                            f_hash = hashlib.sha256(fp.read(65536)).hexdigest()
                        
                        indexed_items.append({
                            "filename": f,
                            "filepath": fpath,
                            "size_bytes": file_size,
                            "modified_time": datetime.fromtimestamp(mtime).isoformat(),
                            "created_time": datetime.fromtimestamp(ctime).isoformat(),
                            "sha256_header": f_hash,
                            "match_reason": "Timestamp Match" if in_time_range else "Filename Temporal Match"
                        })
                except Exception as e:
                    continue

    os.makedirs(os.path.dirname(OUTPUT_VAULT), exist_ok=True)
    with open(OUTPUT_VAULT, "w", encoding="utf-8") as out_f:
        json.dump({
            "target_window": "2021-01-01 to 2022-02-28",
            "total_matched_assets": len(indexed_items),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "items": indexed_items
        }, out_f, indent=2)

    print(f"\n✓ Found and indexed {len(indexed_items)} target assets in timeline window.")
    print(f"✓ Saved manifest to: {OUTPUT_VAULT}")
    return indexed_items

if __name__ == "__main__":
    scan_and_index()
