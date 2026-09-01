#!/usr/bin/env python3
"""
scripts/check_links.py
======================
Automated HTTP status and accessibility scanner for public OSINT URLs,
GitHub Pages dashboards, evidence files, and report manifests.
"""

import urllib.request
import urllib.error
import sys

# List of all your OSINT GitHub and GitHub Pages links
urls = [
    "https://tonypost949.github.io/OsintNeoAi/",
    "https://tonypost949.github.io/OsintNeoAi/gods_eye_view.html",
    "https://tonypost949.github.io/OsintNeoAi/maps_hub.html",
    "https://tonypost949.github.io/OsintNeoAi/master_tactical_gis.html",
    "https://tonypost949.github.io/OsintNeoAi/badass_osint_map.html",
    "https://tonypost949.github.io/OsintNeoAi/comparison_swipe_map.html",
    "https://github.com/Tonypost949/OsintNeoAi",
    "https://github.com/Tonypost949/OsintNeoAi/blob/main/INVESTIGATION_REPORTS_INDEX.md",
    "https://github.com/Tonypost949/OsintNeoAi/blob/main/evidence/caltrans_d12_cctv.geojson",
    "https://github.com/Tonypost949/OsintNeoAi/blob/main/evidence/openosint_nodes.json",
    "https://github.com/Tonypost949/OsintNeoAi/blob/main/evidence/OPENOSINT_1601_Dove_Street.md",
    "https://github.com/Tonypost949/OsintNeoAi/blob/main/evidence/OPENOSINT_17631_Cameron_Lane.md",
    "https://github.com/Tonypost949/OsintNeoAi/blob/main/evidence/OPENOSINT_7561_Center_Ave.md",
    "https://github.com/Tonypost949/OsintNeoAi/blob/main/evidence/OPENOSINT_17642_Beach_Blvd.md"
]

def scan_links():
    print("Scanning OSINT link accessibility...\n" + "="*70)
    
    passed = 0
    failed = 0

    for url in urls:
        try:
            # Using a standard User-Agent prevents GitHub from blocking the automated request
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=12) as response:
                print(f"[ 200 OK ] {url}")
                passed += 1
        except urllib.error.HTTPError as e:
            print(f"[ {e.code} ERROR ] {url}")
            failed += 1
        except urllib.error.URLError as e:
            print(f"[ FAILED ] {e.reason} - {url}")
            failed += 1
        except Exception as ex:
            print(f"[ EXCEPTION ] {ex} - {url}")
            failed += 1

    print("=" * 70)
    print(f"Scan complete: {passed} passed, {failed} failed / pending out of {len(urls)} links.")

if __name__ == "__main__":
    scan_links()
