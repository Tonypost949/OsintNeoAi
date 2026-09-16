import os
from pathlib import Path
from collections import defaultdict
import re

SEARCH_DIRS = [
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/evidence"),
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/data")
]
EXTENSIONS = ['.txt', '.md', '.csv', '.json', '.html']

TARGETS = ["cameron", "17631", "17642", "beach blvd", "hbnc", "shea", "baker", "haick"]
PERMIT_KEYWORDS = ["permit", "grading", "plan check", "inspection", "environmental", "hazmat", "violation"]

def scan_specific_permits():
    print("[+] Extracting detailed permit and contractor records linked to the HBNC site...")
    
    findings = defaultdict(list)
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
                        
                        # Only analyze files that have a site/contractor target AND a permit keyword
                        if any(tk in content for tk in TARGETS) and any(pk in content for pk in PERMIT_KEYWORDS):
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if any(tk in line for tk in TARGETS) and any(pk in line for pk in PERMIT_KEYWORDS):
                                    findings[file].append(f"Line {i+1}: {line.strip()[:300]}")
                except Exception:
                    pass

    print(f"[✓] Scanned {files_scanned} files.")
    
    if not findings:
        print("[-] No detailed permit/contractor records found for the site.")
    else:
        print(f"\n[✓] Found direct contextual matches in {len(findings)} files.")
        
        # We want to print out the most relevant ones (like the geotracker text, or specific JSON records)
        priority_files = [f for f in findings.keys() if "geotracker" in f or "evidence" in f or "hb_urls" not in f]
        
        for file in priority_files[:5]:  # show top 5 priority files to avoid overwhelming the output
            print(f"\n--- MATCHES IN {file} ---")
            for hit in findings[file][:5]:
                print(hit)

if __name__ == "__main__":
    scan_specific_permits()
