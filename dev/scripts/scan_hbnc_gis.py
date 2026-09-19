import os
from pathlib import Path
from collections import defaultdict
import re

SEARCH_DIRS = [
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/evidence"),
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/data"),
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/public"),
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/")
]
EXTENSIONS = ['.txt', '.md', '.csv', '.json', '.html', '.js', '.geojson']

TARGETS = ["cameron", "17631", "17642", "hbnc", "stormtech", "shea", "baker"]
GIS_KEYWORDS = ["gis", "map", "layer", "coordinate", "lat", "lng", "polygon", "geojson", "leaflet", "feature"]

def scan_gis():
    print("[+] Scanning GIS and mapping files for references to HBNC/StormTech/Contractors...")
    
    findings = defaultdict(list)
    files_scanned = 0
    
    for search_dir in SEARCH_DIRS:
        if not search_dir.exists(): continue
        # Don't recurse infinitely if we search root, just go a couple levels deep or target specific folders
        for root, _, files in os.walk(search_dir):
            if 'node_modules' in root or '.git' in root or 'venv' in root: continue
            
            for file in files:
                if Path(file).suffix.lower() not in EXTENSIONS: continue
                filepath = os.path.join(root, file)
                files_scanned += 1
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()
                        
                        # Is it a GIS-related file OR does it contain GIS keywords?
                        is_gis_file = any(gk in file.lower() for gk in GIS_KEYWORDS) or any(gk in content for gk in GIS_KEYWORDS)
                        
                        if is_gis_file and any(tk in content for tk in TARGETS):
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if any(tk in line for tk in TARGETS) and any(gk in line for gk in GIS_KEYWORDS):
                                    findings[file].append(f"Line {i+1}: {line.strip()[:300]}")
                except Exception:
                    pass

    print(f"[✓] Scanned {files_scanned} files.")
    
    if not findings:
        print("[-] No GIS/Mapping references found for the site.")
    else:
        print(f"\n[✓] Found GIS contextual matches in {len(findings)} files.")
        
        # Prioritize files that are actually maps or geojson
        priority_files = [f for f in findings.keys() if f.endswith(".html") or f.endswith(".js") or f.endswith(".geojson") or "map" in f.lower()]
        
        for file in priority_files[:7]:
            print(f"\n--- GIS MATCHES IN {file} ---")
            for hit in findings[file][:5]:
                print(hit)

if __name__ == "__main__":
    scan_gis()
