import os
import re
from pathlib import Path
from collections import defaultdict

HB_URLS_FILE = Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/data/hb_urls_master.txt")
SEARCH_DIRS = [
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/evidence"),
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/data"),
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/docs")
]

# Primary and adjacent addresses, cross streets, and variants
ADDRESS_KEYWORDS = [
    "17631 cameron", "17642 beach", "17631", "17642", "17532 cameron",
    "17621", "17622", "17652", "cameron lane", "beach blvd"
]

# Standard permit patterns (e.g., B20-0123, C19-1234, PMT2019-01234, CUP-19-012)
PERMIT_PATTERN = re.compile(r'\b[A-Z]{1,4}[- ]?(?:20)?\d{2}[- ]?\d{3,6}\b', re.IGNORECASE)

def scan_all_permits():
    print("[+] Compiling exhaustive permit history for HBNC parcels and adjacent addresses...")
    
    # 1. Check HB URLs Master List for Address Matches
    url_hits = set()
    if HB_URLS_FILE.exists():
        with open(HB_URLS_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                url = line.strip().lower()
                # If URL contains the numbers or street names
                if ("17631" in url or "17642" in url or "cameron" in url) and ("permit" in url or "accela" in url or "aca" in url or "record" in url or ".pdf" in url):
                    url_hits.add(line.strip())
                    
    # 2. Scan Evidence for Permit Mentions & Numbers
    evidence_hits = defaultdict(list)
    files_scanned = 0
    
    for search_dir in SEARCH_DIRS:
        if not search_dir.exists(): continue
        for root, _, files in os.walk(search_dir):
            for file in files:
                if not file.endswith(('.txt', '.md', '.csv', '.json', '.html')): continue
                filepath = os.path.join(root, file)
                files_scanned += 1
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines):
                            lower_line = line.lower()
                            
                            # Look for an address match AND the word permit/plan/cert
                            if any(addr in lower_line for addr in ADDRESS_KEYWORDS) and any(pk in lower_line for pk in ["permit", "plan", "certificate", "demolition", "grading"]):
                                # Extract potential permit numbers
                                found_permits = PERMIT_PATTERN.findall(line)
                                if found_permits or "permit" in lower_line:
                                    # Get a short context block
                                    context = " ".join([l.strip() for l in lines[max(0, i-1):min(len(lines), i+2)]])
                                    # Clean up whitespace
                                    context = re.sub(r'\s+', ' ', context)[:250]
                                    evidence_hits[file].append(f"Line {i+1}: Permits {found_permits} | {context}")
                except Exception:
                    pass

    print(f"[✓] Scanned {HB_URLS_FILE.name} (83k+ URLs) and {files_scanned} evidence files.")
    
    print(f"\n[!] MUNICIPAL URL HITS FOR ADJACENT/TARGET ADDRESSES: {len(url_hits)}")
    for url in list(url_hits)[:15]:
        print(f"  - {url}")

    print(f"\n[!] EVIDENCE HITS (PERMITS AT OR NEAR THE PARCEL):")
    
    # Filter to show the most relevant hits that actually extracted a permit number or grading/demo
    meaningful_hits = 0
    for file, hits in evidence_hits.items():
        # Only print if we found an actual permit string like B19-0123 or grading/demo context
        relevant = [h for h in hits if "['" in h or "demo" in h.lower() or "grading" in h.lower()]
        if relevant:
            print(f"\n--- {file} ---")
            for h in relevant[:5]:
                print(f"  {h}")
            meaningful_hits += len(relevant)
            
    if meaningful_hits == 0:
        print("  [-] No explicit permit numbers (B20-XXXX, etc.) found tied to these addresses in the text evidence.")

if __name__ == "__main__":
    scan_all_permits()
