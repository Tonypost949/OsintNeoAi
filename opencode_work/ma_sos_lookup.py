"""
MA Secretary of State / SOS search for TRIUMVIRATE ENVIRONMENTAL INC
MA provides a public business entity search at:
https://corp.sec.state.ma.us/
"""
import subprocess, json
from pathlib import Path

WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")

SEARCHES = [
    ("TRIUMVIRATE ENVIRONMENTAL", "ma_triumvirate_env.json"),
    ("TRIUMVIRATE ENVIRONMENTAL INC", "ma_triumvirate_env2.json"),
    ("TRIUMVIRATE", "ma_triumvirate.json"),
    ("INNER BELT ROAD SOMERVILLE", "ma_innerbelt.json"),
]

for term, outfile in SEARCHES:
    print(f"\n=== MA SOS: {term} ===")
    # Try MA SEC of State corporation search API
    url = f"https://corp.sec.state.ma.us/corpweb/CorpSearch/CorpSearchEntitySearch?SearchTerm={term.replace(' ', '+')}&SearchType=ENT"

    try:
        r = subprocess.run(
            ["curl", "-s", "-L",
             "-H", "Accept: application/json, text/html",
             "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
             "--max-time", "20", url],
            capture_output=True, text=True, timeout=25
        )
        raw = r.stdout.strip()
        print(f"  Raw response (first 500):\n{raw[:500]}")
        if raw and len(raw) > 20:
            # Try to extract entity names
            out = WORK_DIR / outfile
            with open(out, "w") as f:
                f.write(raw)
            print(f"  Saved to {outfile}")
    except Exception as e:
        print(f"  Error: {e}")

    # Also try the CorpNet-style API
    try:
        url2 = f"https://www.sec.state.ma.us/chistocks/CorporateSearch/CorporateSearchEntities?searchTerm={term.replace(' ', '+')}&pageNumber=1&pageSize=10"
        r2 = subprocess.run(
            ["curl", "-s", "-L",
             "-H", "Accept: application/json",
             "-H", "User-Agent: Mozilla/5.0",
             "--max-time", "20", url2],
            capture_output=True, text=True, timeout=25
        )
        raw2 = r2.stdout.strip()
        if raw2 and len(raw2) > 20:
            print(f"  alt API result: {raw2[:500]}")
    except Exception as e:
        print(f"  alt API error: {e}")

# Also search for Somerville MA environmental remediation companies
print("\n=== SEARCH: Somerville MA environmental companies ===")
try:
    url3 = "https://corp.sec.state.ma.us/corpweb/CorpSearch/CorpSearchEntitySearch?SearchTerm=Somerville+environmental&SearchType=ENT"
    r3 = subprocess.run(
        ["curl", "-s", "-L",
         "-H", "User-Agent: Mozilla/5.0",
         "--max-time", "20", url3],
        capture_output=True, text=True, timeout=25
    )
    print(f"  Result: {r3.stdout[:500]}")
except Exception as e:
    print(f"  Error: {e}")

print("\nDone.")
