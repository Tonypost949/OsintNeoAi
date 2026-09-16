import os
import re
import json
from pathlib import Path
from collections import defaultdict

SEARCH_DIRS = [
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/evidence"),
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/data")
]

# Common APN formats in Orange County: 142-261-35, 14226135, etc.
APN_PATTERN = re.compile(r'\b\d{3}[-\s]?\d{3}[-\s]?\d{2}\b')

def scan_radius_historical():
    print("[+] Scanning EDR Lightbox, OCGIS, and historical records for 0.25 mile radius around Cameron/Beach...")
    
    apn_hits = set()
    edr_files = []
    historical_hits = defaultdict(list)
    files_scanned = 0
    
    for search_dir in SEARCH_DIRS:
        if not search_dir.exists(): continue
        for root, _, files in os.walk(search_dir):
            for file in files:
                if not file.endswith(('.txt', '.md', '.csv', '.json', '.html')): continue
                filepath = os.path.join(root, file)
                files_scanned += 1
                
                # Flag EDR / GIS files
                lower_name = file.lower()
                is_edr_or_gis = any(k in lower_name for k in ['edr', 'lightbox', 'ocgis', 'sanborn', 'historical'])
                if is_edr_or_gis:
                    edr_files.append(file)
                
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()
                        
                        # Only process if it hits our target area
                        if "cameron" in content or "17631" in content or "17642" in content or "beach blvd" in content:
                            # Extract APNs
                            apns = APN_PATTERN.findall(content)
                            for apn in apns:
                                apn_hits.add(apn)
                                
                            # If it's an EDR or GIS file, grab context
                            if is_edr_or_gis:
                                lines = content.split('\n')
                                for i, line in enumerate(lines):
                                    if "190" in line or "191" in line or "192" in line or "193" in line or "194" in line or "195" in line or "196" in line or "permit" in line or "sanborn" in line:
                                        if len(line.strip()) > 10:
                                            historical_hits[file].append(f"Line {i+1}: {line.strip()[:200]}")
                except Exception:
                    pass

    print(f"[✓] Scanned {files_scanned} files.")
    print(f"\n[!] EDR Lightbox / OCGIS / Historical Files Detected: {len(edr_files)}")
    print(f"[!] Extracted APNs in proximity to target: {len(apn_hits)}")
    
    # Filter APNs that likely belong to Orange County Tract 142 (Huntington Beach / Cameron area)
    target_apns = [a for a in apn_hits if a.startswith("142")]
    print(f"\n[+] TARGET APN CLUSTER (142-XXX-XX):")
    for a in sorted(target_apns)[:15]:
        print(f"  - {a}")
        
    print(f"\n[+] HISTORICAL EDR & PERMIT HIGHLIGHTS (1900+):")
    meaningful = 0
    for file, hits in historical_hits.items():
        if hits:
            print(f"\n--- {file} ---")
            for h in hits[:5]:
                print(f"  {h}")
            meaningful += 1
            if meaningful > 10: break

if __name__ == "__main__":
    scan_radius_historical()
