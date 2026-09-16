import os
from pathlib import Path
from collections import defaultdict
import re

HB_URLS_FILE = Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/data/hb_urls_master.txt")

# Trying to catch anything related to the "Navigation Center" / "HBNC" / "Mercy House"
TARGET_KEYWORDS = [
    "navigation center", "hbnc", "mercy house", "beach", "cameron", "17631", "17642"
]

def scan_hbnc_urls():
    url_hits = set()
    print("[+] Broadening search in 83,922 HB municipal URLs for the Navigation Center, Mercy House, and Beach/Cameron addresses...")
    
    if HB_URLS_FILE.exists():
        with open(HB_URLS_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                url = line.strip()
                url_lower = url.lower()
                
                # Check for direct mentions of the navigation center or mercy house
                if "navigation" in url_lower or "hbnc" in url_lower or "mercy" in url_lower:
                    if ".pdf" in url_lower or "report" in url_lower or "plan" in url_lower or "permit" in url_lower:
                        url_hits.add(url)
                        
    if url_hits:
        print(f"\n[✓] Found {len(url_hits)} direct municipal URLs tied to the Navigation Center / HBNC.")
        for url in sorted(url_hits):
            print(f"  - {url}")
    else:
        print("[-] No specific URLs found.")

if __name__ == "__main__":
    scan_hbnc_urls()
