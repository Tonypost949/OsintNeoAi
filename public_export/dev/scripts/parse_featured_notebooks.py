#!/usr/bin/env python3
"""
parse_featured_notebooks.py — Parse Google NotebookLM Featured/Discover Public Library
"""

import re
import json

HTML_FILE = r"C:\Users\Amd949609\Downloads\Gemini Notebook featured.html"
OUTPUT_JSON = r"C:\OsintNeoAi\data\featured_public_notebooks_catalog.json"

def main():
    with open(HTML_FILE, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    pattern = re.compile(r'<a[^>]*class="project-table-title"[^>]*title="([^"]+)"[^>]*href="([^"]+)"', re.IGNORECASE)
    matches = pattern.findall(content)

    featured = []
    for title, url in matches:
        clean_url = url.replace("notebook.google.com", "notebooklm.google.com")
        uuid = url.split("/")[-1]
        featured.append({"title": title.strip(), "uuid": uuid, "url": clean_url})

    print(f"[+] Found {len(featured)} public featured notebook workspaces:")
    for f in featured:
        print(f"  • {f['title']}: {f['url']}")

    with open(OUTPUT_JSON, "w", encoding="utf-8") as out:
        json.dump({"total": len(featured), "notebooks": featured}, out, indent=2)

    print(f"[+] Saved featured catalog to: {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
