import os
import re
import json
from pathlib import Path
from collections import defaultdict

SEARCH_DIRS = [
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/evidence"),
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/data")
]

APNS = [
    "142-073-33", "142-073-54", "142-075-01", "142-075-02", 
    "142-082-35", "142-122-07", "142-242-16", "142-253-04", 
    "142-321-20", "142-492-11", "14205653", "14206304", 
    "14216029", "14220790", "14235693", "142-261"
]

def scan_edr_and_apns():
    print("[+] Extracting EDR Lightbox, Sanborn Maps, and APN histories back to 1900...")
    hits = defaultdict(list)
    files_scanned = 0
    
    # We will search specifically for our target APNs OR mentions of 19XX permits
    for search_dir in SEARCH_DIRS:
        if not search_dir.exists(): continue
        for root, _, files in os.walk(search_dir):
            for file in files:
                if not file.endswith(('.txt', '.md', '.csv', '.json', '.html')): continue
                filepath = os.path.join(root, file)
                files_scanned += 1
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()
                        
                        # First pass: check if file contains any of our APNs
                        if any(apn.replace("-", "") in content.replace("-", "") for apn in APNS) or "sanborn" in content or "lightbox" in content or "edr " in content:
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                # If it mentions an APN, Sanborn, EDR, or a 19XX date
                                if any(apn.replace("-", "") in line.replace("-", "") for apn in APNS) or re.search(r'\b19[0-9]{2}\b', line) or "sanborn" in line or "lightbox" in line:
                                    # Grab context
                                    start = max(0, i - 1)
                                    end = min(len(lines), i + 2)
                                    block = " ".join([l.strip() for l in lines[start:end]])
                                    block = re.sub(r'\s+', ' ', block)[:350]
                                    hits[file].append(f"Line {i+1}: {block}")
                except Exception:
                    pass

    print(f"[✓] Scanned {files_scanned} files.")
    
    out_path = "C:/Users/Amd949609/StudioProjects/OsintNeoAi/data/edr_apn_historical_data.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(hits, f, indent=2)
    print(f"\n[✓] EDR Historical extraction complete. Dumped {len(hits)} files with hits to {out_path}")

if __name__ == '__main__':
    scan_edr_and_apns()
