#!/usr/bin/env python3
"""
compact_crossref_matrix.py — Cap JSON size under GitHub 100MB limit
"""

import json
from pathlib import Path

MATCHES_FILE = r"C:\OsintNeoAi\data\master_accounts_crossref_matches.json"

def main():
    if not Path(MATCHES_FILE).exists():
        return
    with open(MATCHES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict) and "full_matches" in data:
        # Keep top 50 matches per account in full_matches to keep file under 5MB
        capped_matches = {}
        for target, matches in data["full_matches"].items():
            capped_matches[target] = matches[:50]
        data["full_matches"] = capped_matches
        data["note"] = "Capped at 50 sample links per target in git repo to meet GitHub <100MB file limit."

        with open(MATCHES_FILE, "w", encoding="utf-8") as out:
            json.dump(data, out, indent=2)
        print(f"[+] Successfully compacted {MATCHES_FILE} to {Path(MATCHES_FILE).stat().st_size / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    main()
