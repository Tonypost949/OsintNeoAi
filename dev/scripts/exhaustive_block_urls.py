import os
import re
from pathlib import Path
from collections import defaultdict

# The list of ALL 83,922 URLs from the HB municipal system we have locally
HB_URLS_FILE = Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/data/hb_urls_master.txt")

def exhaustive_url_extraction():
    print("[+] Performing exhaustive, wildcard extraction across the 83,922 HB municipal URLs for the target block...")
    
    # We will search for ANY mention of the street names in the URL structure.
    # Often, municipal permit URLs encode the address (e.g., /permits/cameron-17631.pdf)
    target_kws = ["cameron", "17631", "17642", "17532", "17621", "17622", "17652"]
    
    hits = set()
    
    if HB_URLS_FILE.exists():
        with open(HB_URLS_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                url = line.strip()
                url_lower = url.lower()
                
                # If the URL contains Cameron OR any of the block numbers
                if "cameron" in url_lower or any(num in url_lower for num in ["17631", "17642", "17532", "17621", "17622", "17652"]):
                    # To avoid false positives on random numbers, if it's just a number, ensure it has context like "beach" or "cameron" or "permit"
                    if "cameron" in url_lower or "beach" in url_lower or "permit" in url_lower or "accela" in url_lower or "plan" in url_lower:
                        hits.add(url)
                        
    if hits:
        print(f"\n[✓] Found {len(hits)} exact or adjacent municipal URLs on the target block.")
        for hit in sorted(hits):
            print(f"  - {hit}")
    else:
        print("[-] Absolutely zero municipal URLs found for the target block.")

if __name__ == "__main__":
    exhaustive_url_extraction()
