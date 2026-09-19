import os
import json
from pathlib import Path
from collections import defaultdict

# The exact list of keywords you provided earlier today across the repository
TARGETS = [
    "Harvest Small Business Finance",
    "Harvest",
    "JPMorgan",
    "Maricopa",
    "Woodbridge",
    "11770 WARNER AVENUE",
    "Anaheim First",
    "Visit Anaheim",
    "Clay M. Smith",
    "Mercy House"
]

EVIDENCE_DIR = Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/evidence")
OUTPUT_FILE = Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/data/custom_keyword_leads.json")

def scan_evidence():
    print(f"[+] Starting deep evidence scan for {len(TARGETS)} specific keywords without using any APIs...")
    
    findings = defaultdict(list)
    files_scanned = 0
    hits_found = 0

    # Scan readable text to prevent binary hangs, completely local CPU execution (no API limits)
    search_extensions = ['.txt', '.md', '.csv', '.json', '.html']
    targets_lower = [t.lower() for t in TARGETS]
    
    for root, dirs, files in os.walk(EVIDENCE_DIR):
        for file in files:
            ext = Path(file).suffix.lower()
            if ext not in search_extensions:
                continue
                
            filepath = os.path.join(root, file)
            files_scanned += 1
            
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                    
                    for original_kw, kw_lower in zip(TARGETS, targets_lower):
                        if kw_lower in content:
                            findings[original_kw].append(str(Path(filepath).relative_to(EVIDENCE_DIR)))
                            hits_found += 1
            except Exception:
                pass
                
    print(f"[✓] Scanned {files_scanned} files locally.")
    print(f"[✓] Found {hits_found} target matches.")
    
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            "scan_metadata": {
                "files_scanned": files_scanned,
                "total_hits": hits_found,
                "targets_used": TARGETS
            },
            "findings": findings
        }, f, indent=2)
        
    print(f"[✓] Extracted intelligence saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    scan_evidence()
