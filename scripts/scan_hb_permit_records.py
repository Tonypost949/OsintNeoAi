import os
import json
from pathlib import Path
import re

SEARCH_DIRS = [
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/evidence"),
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/data"),
]
# Keywords targeting excavation permits, hazmat, building plans at HBNC addresses
PERMIT_KEYWORDS = ["permit", "grading", "building", "plan check", "inspection", "accela", "citizenaccess", "aca", "environmental", "hazmat"]
TARGET_KEYWORDS = ["cameron", "17631", "17642", "beach", "stormtech"]
EXTENSIONS = ['.txt', '.md', '.csv', '.json', '.html']

def scan_for_direct_permit_records():
    print("[+] Scanning for direct Huntington Beach municipal permit records for Cameron/Beach Blvd...")
    files_scanned = 0
    permit_hits = set()
    
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
                        # Require a target keyword AND a permit keyword
                        if any(tk in content for tk in TARGET_KEYWORDS) and any(pk in content for pk in PERMIT_KEYWORDS):
                            lines = content.split('\n')
                            for line in lines:
                                if any(tk in line for tk in TARGET_KEYWORDS) and any(pk in line for pk in PERMIT_KEYWORDS):
                                    permit_hits.add(f"{Path(filepath).name}: {line.strip()[:200]}")
                except Exception:
                    pass
                    
    print(f"[✓] Scanned {files_scanned} files.")
    
    if permit_hits:
        print(f"\n[✓] Found {len(permit_hits)} specific permit/record mentions linked to the site.")
        for hit in list(permit_hits)[:30]:
             print(hit)
    else:
        print("[-] No direct permit record mentions found.")

if __name__ == "__main__":
    scan_for_direct_permit_records()
