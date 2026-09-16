import os
import json
from pathlib import Path
import re

SEARCH_DIRS = [
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/evidence"),
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/data"),
]
# Keywords that would identify Huntington Beach permit systems or document repositories
PERMIT_URL_KEYWORDS = [
    "huntingtonbeachca.gov", "hb.net", "accela", "citizenaccess", 
    "permits", "building", "plan check", "inspection", "aca"
]
EXTENSIONS = ['.txt', '.md', '.csv', '.json', '.html']

def scan_for_permit_links():
    print("[+] Scanning for Huntington Beach permit system URLs and document links...")
    permit_links = set()
    files_scanned = 0
    
    for search_dir in SEARCH_DIRS:
        if not search_dir.exists(): continue
        for root, _, files in os.walk(search_dir):
            for file in files:
                if Path(file).suffix.lower() not in EXTENSIONS: continue
                filepath = os.path.join(root, file)
                files_scanned += 1
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()
                        # Quick check if file might contain our keywords
                        if any(kw in content for kw in PERMIT_URL_KEYWORDS):
                            # Extract URLs
                            urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
                            for url in urls:
                                if "huntington" in url or "accela" in url or "permit" in url:
                                     permit_links.add(url)
                except Exception:
                    pass
                    
    print(f"[✓] Scanned {files_scanned} files.")
    
    if not permit_links:
        print("[-] No HB permit links found.")
    else:
        print(f"\n[✓] Found {len(permit_links)} unique HB permit/municipal system URLs.")
        print("\n--- SAMPLE URLs ---")
        for link in list(permit_links)[:20]:
             print(link)

if __name__ == "__main__":
    scan_for_permit_links()
