import os
import re
from pathlib import Path

HB_URLS_FILE = Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/data/hb_urls_master.txt")
OUTPUT_FILE = Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/data/hbnc_permit_urls.txt")

def find_hbnc_permits():
    if not HB_URLS_FILE.exists():
        print(f"[-] {HB_URLS_FILE} not found.")
        return

    print(f"[+] Scanning 83,922 URLs for HBNC / Cameron / 17631 / 17642 permits and documents...")
    
    hbnc_links = set()
    
    # We are looking for URLs that relate to the property OR specific permit types (grading, building) at those addresses
    target_keywords = ["cameron", "17631", "17642", "hbnc", "navigation", "beach blvd"]
    permit_keywords = ["permit", "grading", "building", "plan", "inspection", "accela", "citizenaccess", "aca", "environmental"]
    
    with open(HB_URLS_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            url = line.strip().lower()
            # If the URL contains an HBNC target AND is a document or permit type
            if any(tk in url for tk in target_keywords):
                # We also want to catch any PDFs or specific documents related to these addresses
                if any(pk in url for pk in permit_keywords) or url.endswith(".pdf"):
                    hbnc_links.add(line.strip())

    if hbnc_links:
        print(f"\n[✓] Found {len(hbnc_links)} permit/document URLs explicitly tied to the HBNC site.")
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            for link in sorted(hbnc_links):
                f.write(link + "\n")
        
        print("\n--- SAMPLE URLs ---")
        for link in list(hbnc_links)[:15]:
            print(link)
        print(f"\n[✓] Full list saved to {OUTPUT_FILE}")
    else:
        print("[-] No HBNC-specific permit links found.")

if __name__ == "__main__":
    find_hbnc_permits()
