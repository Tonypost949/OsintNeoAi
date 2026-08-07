"""
CA SOS Business Search - trying multiple API approaches
"""
import subprocess, json
from pathlib import Path

WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")

SEARCHES = [
    "TRIUMVIRATE LLC",
    "TS MARKETPLACE LLC",
    "19822 BROOKHURST LLC",
    "RAI PARTNERS LLC",
    "HRAPTS1 LLC",
    "ROSELL",
    "STEWART INDUSTRIES LLC",
    "L2T MEDIA LLC",
    "19822 BROOKHURST",
    "333 WASHINGTON BLVD MARINA DEL REY",
]

for term in SEARCHES:
    print(f"\n=== Searching: {term} ===")
    # Try 1: sosca.gov search API
    try:
        url = f"https://businesssearch.sos.ca.gov/api/v1/search?name={term.replace(' ', '%20')}&type=&status="
        r = subprocess.run(
            ["curl", "-s", "-L", "-H", "Accept: application/json",
             "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
             "--max-time", "15", url],
            capture_output=True, text=True, timeout=20
        )
        raw = r.stdout.strip()
        if raw and raw.startswith("{"):
            data = json.loads(raw)
            print(f"  API v1 result: {str(data)[:300]}")
        else:
            print(f"  API v1 empty/invalid")
    except Exception as e:
        print(f"  API v1 error: {e}")

    # Try 2: businesssearch.sos.ca.gov
    try:
        url2 = f"https://businesssearch.sos.ca.gov/api?name={term.replace(' ', '%20')}&entityType=&status=Active"
        r2 = subprocess.run(
            ["curl", "-s", "-L", "-H", "Accept: application/json",
             "-H", "Referer: https://businesssearch.sos.ca.gov/",
             "--max-time", "15", url2],
            capture_output=True, text=True, timeout=20
        )
        raw2 = r2.stdout.strip()
        if raw2 and len(raw2) > 10:
            print(f"  businesssearch result: {raw2[:500]}")
        else:
            print(f"  businesssearch empty")
    except Exception as e:
        print(f"  businesssearch error: {e}")

    # Try 3: direct web scrape of bizfileonline
    try:
        search_url = f"https://bizfileonline.sos.ca.gov/search/search?searchType=entity&searchName={term.replace(' ', '+')}&status=Active"
        r3 = subprocess.run(
            ["curl", "-s", "-L", "-H", "User-Agent: Mozilla/5.0",
             "--max-time", "15", search_url],
            capture_output=True, text=True, timeout=20
        )
        raw3 = r3.stdout.strip()
        if raw3 and len(raw3) > 50:
            print(f"  bizfileonline result: {raw3[:300]}")
        else:
            print(f"  bizfileonline empty")
    except Exception as e:
        print(f"  bizfileonline error: {e}")

print("\nDone.")
