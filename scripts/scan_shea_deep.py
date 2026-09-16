import os
import json
from pathlib import Path
from collections import defaultdict

SEARCH_DIRS = [
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/evidence"),
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/data"),
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/docs"),
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/AiRiCOSwarm/reports")
]
KEYWORDS = ["shea", "j.f. shea", "jf shea", "michael baker", "contractor"]
EXTENSIONS = ['.txt', '.md', '.csv', '.json', '.html']

def scan_deep():
    print("[+] Deep scanning for Shea / Michael Baker specific context linkages to Cameron/HBNC...")
    findings = []
    
    for search_dir in SEARCH_DIRS:
        if not search_dir.exists(): continue
        for root, _, files in os.walk(search_dir):
            for file in files:
                if Path(file).suffix.lower() not in EXTENSIONS: continue
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()
                        # Narrow down to files that mention shea/baker AND cameron/hbnc
                        if any(k in content for k in KEYWORDS) and ("cameron" in content or "hbnc" in content or "17631" in content or "17642" in content):
                            findings.append(file)
                except Exception:
                    pass
    
    print(f"\n[✓] Found {len(set(findings))} files mentioning both Shea/Contractors AND the HBNC/Cameron site.")
    for f in set(findings):
        print(f"    - {f}")

if __name__ == "__main__":
    scan_deep()
