#!/usr/bin/env python3
"""
extract_all_notebook_urls.py — Extract direct URLs for all 42 Notebooks from catalogue HTML
"""

import re
import json
from pathlib import Path

HTML_FILE = r"C:\Users\Amd949609\Downloads\Gemini Notebook.html"
OUTPUT_JSON = r"C:\OsintNeoAi\data\all_42_notebooklm_urls.json"

def main():
    with open(HTML_FILE, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    pattern = re.compile(r'id=["\']project-([a-f0-9\-]{36})-title["\'][^>]*>\s*([^<]+)\s*</span>', re.IGNORECASE)
    matches = pattern.findall(content)

    print(f"[+] Successfully extracted {len(matches)} notebook UUIDs and direct URLs from Catalogue HTML:")
    notebook_links = []
    for uuid, title in matches:
        title_clean = title.strip()
        url = f"https://notebooklm.google.com/notebook/{uuid}"
        notebook_links.append({
            "title": title_clean,
            "uuid": uuid,
            "url": url
        })
        print(f"  • {title_clean}: {url}")

    output_data = {
        "total": len(notebook_links),
        "account": "amd949609@gmail.com",
        "notebooks": notebook_links
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as out:
        json.dump(output_data, out, indent=2)

    print(f"[+] Saved to: {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
