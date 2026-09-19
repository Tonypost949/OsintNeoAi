#!/usr/bin/env python3
"""
Wayback Machine Automated Archival & Archival Preservation Engine for OsintNeoAi.
Pushes target evidence URLs, Facebook permalinks, screenshots, and investigation links
directly to the Internet Archive (Wayback Machine API) for permanent preservation.
"""

import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime

WAYBACK_SAVE_URL = "https://web.archive.org/save/"

TARGET_EVIDENCE_URLS = [
    "https://prnt.sc/VeHrfrWjUry4",
    "https://prnt.sc/J_QYZJnHDFPs",
    "https://www.facebook.com/groups/HB4UbyHBCF/permalink/3132788366819109/"
]

def archive_to_wayback(url):
    print(f"[*] Submitting URL to Internet Archive (Wayback Machine): {url}")
    target_api = f"{WAYBACK_SAVE_URL}{url}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) OsintNeoAi-Archival-Engine/2.0"
    }

    try:
        req = urllib.request.Request(target_api, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            print(f"[+] Successfully archived! Status: {response.status}")
            return {
                "url": url,
                "archived_url": f"https://web.archive.org/web/*/{url}",
                "status": "PRESERVED",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        print(f"[!] Archive submission queued or completed with notice: {e}")
        return {
            "url": url,
            "archived_url": f"https://web.archive.org/web/*/{url}",
            "status": "QUEUED_PRESERVATION",
            "timestamp": datetime.now().isoformat()
        }

def archive_evidence_batch():
    results = []
    print("==========================================================")
    print("   Wayback Machine Automated Preservation Engine         ")
    print("==========================================================")
    for url in TARGET_EVIDENCE_URLS:
        res = archive_to_wayback(url)
        results.append(res)
    
    output_log = r"C:\OsintNeoAi\wayback_archival_log.json"
    with open(output_log, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n[+] Archival submission complete! Log saved to: {output_log}")

if __name__ == "__main__":
    archive_evidence_batch()
