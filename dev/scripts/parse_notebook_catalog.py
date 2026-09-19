#!/usr/bin/env python3
"""
parse_notebook_catalog.py — Parse NotebookLM Master Dashboard Export
Extracts all notebook names, dates, and source counts from the saved dashboard HTML.
"""

import re
import json
from pathlib import Path

TXT_FILE = r"C:\OsintNeoAi\data\chats\notebooks\Gemini_Notebook_extracted.txt"
OUTPUT_JSON = r"C:\OsintNeoAi\data\notebooklm_all_notebooks_catalog.json"

def parse():
    with open(TXT_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    catalog = []
    i = 0
    while i < len(lines):
        if i + 3 < len(lines) and "source" in lines[i+3] and lines[i+2] == "·":
            title = lines[i]
            date = lines[i+1]
            sources_str = lines[i+3]
            match = re.search(r"(\d+)\s+source", sources_str)
            count = int(match.group(1)) if match else 0
            catalog.append({"title": title, "date": date, "source_count": count})
            i += 4
        else:
            i += 1

    total_sources = sum(c["source_count"] for c in catalog)
    print(f"[+] Discovered {len(catalog)} total NotebookLM notebooks ({total_sources} total sources):")
    for item in catalog:
        print(f"  • {item['title']} — {item['source_count']} sources ({item['date']})")

    output = {
        "account": "amd949609@gmail.com",
        "total_notebooks": len(catalog),
        "total_sources_across_all_notebooks": total_sources,
        "notebooks": catalog
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as out:
        json.dump(output, out, indent=2)

    print(f"[+] Saved catalog to: {OUTPUT_JSON}")

if __name__ == "__main__":
    parse()
