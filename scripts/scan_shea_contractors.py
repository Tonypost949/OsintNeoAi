import os
from pathlib import Path
from collections import defaultdict
import re

SEARCH_DIRS = [
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/evidence"),
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/data"),
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/docs"),
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/AiRiCOSwarm/reports")
]
TARGET_ENTITIES = ["shea", "j.f. shea", "jf shea", "baker", "michael baker", "contractor", "hauler", "excavation", "remediation"]
CONTEXT_KEYWORDS = ["stormtech", "storm tech", "cameron", "hbnc", "17631", "17642", "beach blvd", "waste", "sinkhole", "geotracker"]
EXTENSIONS = ['.txt', '.md', '.csv', '.json', '.html']

def scan_for_contractors():
    print("[+] Scanning for contractors/hauling entities (specifically Shea) linked to HBNC/StormTech excavation...")
    findings = defaultdict(set)
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
                        
                        # Only analyze files that mention our context (HBNC/Cameron/Stormtech) AND a target entity
                        if any(ck in content for ck in CONTEXT_KEYWORDS) and any(te in content for te in TARGET_ENTITIES):
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                # If the line specifically mentions shea/contractors
                                if any(te in line for te in TARGET_ENTITIES):
                                    # Grab surrounding context lines (up to 2 before and 2 after)
                                    start = max(0, i - 2)
                                    end = min(len(lines), i + 3)
                                    context_block = " ".join([lines[j].strip() for j in range(start, end)])
                                    
                                    # If the block contains our context keywords
                                    if any(ck in context_block for ck in CONTEXT_KEYWORDS):
                                        findings[file].add(f"Line {i+1}: {line.strip()[:200]}")
                except Exception:
                    pass
                    
    print(f"[✓] Scanned {files_scanned} files.")
    
    if not findings:
        print("[-] No direct linkages found connecting Shea or other contractors to the HBNC excavation in the same context block.")
    else:
        for file, hits in findings.items():
            print(f"\n--- MATCHES IN {file} ---")
            for hit in hits:
                print(hit)

if __name__ == "__main__":
    scan_for_contractors()
