import os
from pathlib import Path
import re

SEARCH_DIRS = [
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/evidence"),
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/data"),
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/docs")
]
EXTENSIONS = ['.txt', '.md', '.csv', '.json', '.html']

def extract_exact_permits():
    print("[+] Hunting for exact Permit Numbers, Grading Permits, and Waste Manifests for the HBNC excavation...")
    
    hits = []
    # Regex to catch typical permit formats (e.g., B20-0123, C19-4567, grading permit, SWPPP, WDID)
    permit_patterns = [
        r'\b[A-Z]{1,2}\d{2}-\d{4,6}\b',  # standard permit format
        r'permit\s+(?:no\.?|number|#)?\s*[A-Z0-9-]{5,}', 
        r'grading permit', 
        r'building permit', 
        r'excavation permit',
        r'waste manifest',
        r'wdid\s*\d+',
        r'swppp',
        r'well-destruction permit',
        r'well destruction permit'
    ]
    
    # We want these permits to specifically relate to the target site
    target_kws = ["17631", "17642", "cameron", "hbnc", "stormtech", "beach blvd", "excavation", "haick", "baker"]
    
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
                        # File must mention the site/contractors AND the word permit/manifest
                        if any(tk in content for tk in target_kws) and ("permit" in content or "manifest" in content or "swppp" in content):
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if any(tk in line for tk in target_kws) or any(re.search(pat, line) for pat in permit_patterns):
                                    # If line mentions a permit or site, check context window (3 lines) for the intersection
                                    start = max(0, i - 1)
                                    end = min(len(lines), i + 2)
                                    block = " ".join(lines[start:end])
                                    if any(tk in block for tk in target_kws) and any(re.search(pat, block) for pat in permit_patterns):
                                        # Extract the exact permit string if possible
                                        found_permits = []
                                        for pat in permit_patterns:
                                            found_permits.extend(re.findall(pat, block))
                                        
                                        if found_permits:
                                            hits.append({
                                                "file": file,
                                                "line": i+1,
                                                "permits": list(set(found_permits)),
                                                "context": line.strip()[:200]
                                            })
                except Exception:
                    pass

    # Deduplicate and print
    unique_hits = {f"{h['file']}_{h['context']}": h for h in hits}.values()
    print(f"[✓] Scanned {files_scanned} files.")
    
    if not unique_hits:
        print("[-] No exact permit records matched the criteria.")
    else:
        print(f"\n[✓] Found exact permit correlations in evidence:")
        # Sort to prioritize files that look like official dossiers or geotracker docs
        for hit in sorted(unique_hits, key=lambda x: x['file']):
            print(f"\nFILE: {hit['file']} (Line {hit['line']})")
            print(f"PERMITS/KEYWORDS FOUND: {hit['permits']}")
            print(f"CONTEXT: {hit['context']}")

if __name__ == "__main__":
    extract_exact_permits()
