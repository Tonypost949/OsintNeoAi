#!/usr/bin/env python3
"""
open_notebooks_in_browser.py — 1-Command Browser Batch Tab Opener
Opens NotebookLM workspaces in default browser tabs in batches.
"""

import sys
import time
import json
import webbrowser
import argparse

CATALOG_FILE = r"C:\OsintNeoAi\data\all_42_notebooklm_urls.json"

def main():
    parser = argparse.ArgumentParser(description="Open NotebookLM workspaces in browser tabs.")
    parser.add_argument("--batch", choices=["top5", "top10", "all", "range"], default="top5", help="Batch to open")
    parser.add_argument("--start", type=int, default=0, help="Start index for range")
    parser.add_argument("--end", type=int, default=5, help="End index for range")
    args = parser.parse_args()

    with open(CATALOG_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    notebooks = data.get("notebooks", [])
    if args.batch == "top5":
        targets = notebooks[:5]
    elif args.batch == "top10":
        targets = notebooks[:10]
    elif args.batch == "all":
        targets = notebooks
    elif args.batch == "range":
        targets = notebooks[args.start:args.end]

    print(f"[*] Opening {len(targets)} NotebookLM tabs in browser...")
    for nb in targets:
        print(f"  -> Opening: {nb['title']} ({nb['url']})")
        webbrowser.open(nb["url"])
        time.sleep(0.3)

    print("[+] All requested tabs launched!")

if __name__ == "__main__":
    main()
