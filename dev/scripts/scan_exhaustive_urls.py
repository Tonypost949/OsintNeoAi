import os
import re
from pathlib import Path
from collections import defaultdict

HB_URLS_FILE = Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/data/hb_urls_master.txt")

# Target APNs for the area around Cameron Lane/Beach Blvd based on previous searches
# Also adding historical names like 'Huntington Beach Lofts', 'Fairwind'
ADDRESS_KEYWORDS = [
    "17631 cameron", "17642 beach", "17631", "17642", "17532 cameron",
    "17621", "17622", "17652", "cameron lane", "beach blvd",
    "huntington beach lofts", "fairwind"
]

def scan_urls_exhaustively():
    url_hits = set()
    print("[+] Scanning all 83,922 HB municipal URLs for the target addresses, APNs, and historical names...")
    
    if HB_URLS_FILE.exists():
        with open(HB_URLS_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                url = line.strip().lower()
                
                # Check if URL contains any of the address identifiers
                if any(addr in url for addr in ADDRESS_KEYWORDS) or ("142-261" in url): # Catching the APN block
                    
                    # We are only interested in permits, plans, env reports, building docs
                    if any(pk in url for pk in ["permit", "plan", "env", "report", "build", "safet", "cert", "accela", "aca", ".pdf", "project"]):
                        url_hits.add(line.strip())
                        
    if url_hits:
        print(f"\n[✓] Found {len(url_hits)} direct municipal URLs tied to the target addresses/developments.")
        for url in sorted(url_hits):
            print(f"  - {url}")
    else:
        print("[-] No specific URLs found.")

if __name__ == "__main__":
    scan_urls_exhaustively()
