"""
Corrected CA SOS Business Search API
https://businesssearch.sos.ca.gov/ is the web interface
API endpoint: https://businesssearch.sos.ca.gov/api/v1/search
"""
import subprocess, json
from pathlib import Path

WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")

SEARCHES = [
    "Mercy House Living Centers Inc",
    "Casa Aliento LP",
    "Hoang Sweden LLC",
    "Jaric Properties LLC",
    "Ares Investment Group LLC",
    "West Continental Properties LLC",
    "Century Housing Corporation",
    "Mercy Ceal Inc",
    "2Nd And B Mercy House CHDO LLC",
]

for term in SEARCHES:
    print(f"\nSearching CA SOS: {term}")
    # Try the correct SOS API endpoint
    url = f"https://businesssearch.sos.ca.gov/api/v1/search?name={term.replace(' ', '%20')}&type=LP%2CLLC%2CCorporation&status=Active"
    try:
        r = subprocess.run(
            ["curl", "-s", "-L", "-H", "Accept: application/json", "--max-time", "15", url],
            capture_output=True, text=True, timeout=20
        )
        raw = r.stdout.strip()
        print(f"  Raw response (first 500): {raw[:500]}")
        try:
            data = json.loads(raw)
            outfile = WORK_DIR / f"sos_{term.lower().replace(' ', '_').replace('&', '')}.json"
            with open(outfile, "w") as f:
                json.dump(data, f, indent=2)
            # Try to extract businesses
            businesses = data.get("results", data.get("businesses", []))
            if isinstance(businesses, list):
                print(f"  -> {len(businesses)} results")
                for b in businesses:
                    print(f"     {b}")
            else:
                print(f"  Response: {str(data)[:200]}")
        except json.JSONDecodeError:
            print(f"  Non-JSON response: {raw[:200]}")
    except Exception as e:
        print(f"  ERROR: {e}")

print("\nDone.")
