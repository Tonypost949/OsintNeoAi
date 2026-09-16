import os
import re
import json
from pathlib import Path
from collections import defaultdict
import time

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

# Pre-compile APN patterns (no dashes for matching)
APN_NODASH = [apn.replace("-", "") for apn in APNS]
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB limit
EXTENSIONS = {'.txt', '.md', '.csv', '.json', '.html'}

def scan_edr_and_apns():
    print("[+] Extracting EDR Lightbox, Sanborn Maps, and APN histories back to 1900...")
    hits = defaultdict(list)
    files_scanned = 0
    files_skipped = 0
    start_time = time.time()
    
    for search_dir in SEARCH_DIRS:
        if not search_dir.exists(): 
            print(f"  [!] Directory not found: {search_dir}")
            continue
        
        print(f"  [-] Scanning {search_dir}...")
        for root, _, files in os.walk(search_dir):
            for file in files:
                if not any(file.endswith(ext) for ext in EXTENSIONS):
                    continue
                
                filepath = os.path.join(root, file)
                
                # Skip large files
                try:
                    if os.path.getsize(filepath) > MAX_FILE_SIZE:
                        files_skipped += 1
                        continue
                except:
                    continue
                
                files_scanned += 1
                if files_scanned % 100 == 0:
                    elapsed = time.time() - start_time
                    print(f"  [-] Progress: {files_scanned} files scanned ({elapsed:.1f}s)...")
                
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        content_lower = content.lower()
                        
                        # Fast check: does file contain any APN or keywords?
                        has_apn = any(apn in content_lower for apn in APN_NODASH)
                        has_keyword = "sanborn" in content_lower or "lightbox" in content_lower or "edr " in content_lower
                        
                        if not has_apn and not has_keyword:
                            continue
                        
                        # File matched - extract relevant lines
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            line_lower = line.lower()
                            
                            # Check for APN match
                            apn_match = any(apn in line_lower for apn in APN_NODASH)
                            # Check for year pattern (1900-1999)
                            year_match = bool(re.search(r'\b19[0-9]{2}\b', line))
                            # Check for keywords
                            keyword_match = "sanborn" in line_lower or "lightbox" in line_lower
                            
                            if apn_match or year_match or keyword_match:
                                # Grab context (1 line before and after)
                                start = max(0, i - 1)
                                end = min(len(lines), i + 2)
                                block = " ".join([l.strip() for l in lines[start:end]])
                                block = re.sub(r'\s+', ' ', block)[:300]
                                
                                # Tag the hit type
                                tags = []
                                if apn_match: tags.append("APN")
                                if year_match: tags.append("YEAR")
                                if keyword_match: tags.append("KEYWORD")
                                
                                hits[file].append({
                                    "line": i + 1,
                                    "tags": tags,
                                    "context": block
                                })
                                
                except Exception as e:
                    pass

    elapsed = time.time() - start_time
    print(f"\n[✓] Scan complete: {files_scanned} files scanned, {files_skipped} skipped (>{MAX_FILE_SIZE//1024//1024}MB), {elapsed:.1f}s")
    
    # Deduplicate hits per file
    for file in hits:
        seen = set()
        unique = []
        for hit in hits[file]:
            key = (hit["line"], hit["context"][:50])
            if key not in seen:
                seen.add(key)
                unique.append(hit)
        hits[file] = unique
    
    out_path = "C:/Users/Amd949609/StudioProjects/OsintNeoAi/data/edr_apn_historical_data.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(dict(hits), f, indent=2)
    
    total_hits = sum(len(v) for v in hits.values())
    print(f"[✓] EDR Historical extraction complete: {total_hits} hits across {len(hits)} files")
    print(f"[✓] Output: {out_path}")

if __name__ == '__main__':
    scan_edr_and_apns()
