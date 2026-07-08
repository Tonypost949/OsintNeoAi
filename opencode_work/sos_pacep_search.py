"""
PACEP + CA SOS + LLC Owner Investigation
Targets:
  - Mercy House CHDO entity addresses
  - Casa Aliento LP beneficial owners
  - HOANG SWEDEN LLC owners
  - JARIC PROPERTIES LLC owners
  - ARES INVESTMENT GROUP LLC owners
  - BEACH BLVD / CENTER AVE LLC owners
"""

import subprocess, json
from pathlib import Path

WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")

# CA SOS Business Search API
# https://businesssearch.sos.ca.gov/

SEARCHES = [
    ("MERCY HOUSE LIVING CENTERS", "mercy_house_sos.json"),
    ("CASA ALIENTO LP", "casa_aliento_sos.json"),
    ("HOANG SWEDEN LLC", "hoang_sweden_sos.json"),
    ("JARIC PROPERTIES LLC", "jaric_sos.json"),
    ("ARES INVESTMENT GROUP LLC", "ares_sos.json"),
    ("WEST CONTINENTAL PROPERTIES LLC", "west_continental_sos.json"),
    ("AFFORDABLE HOUSING LAND CONSULTANTS LLC", "affordable_housing_sos.json"),
    ("CENTURY HOUSING CORPORATION", "century_housing_sos.json"),
    ("BANC OF CALIFORNIA", "banc_california_sos.json"),
    ("MERCEAL INC", "mercy_ceal_sos.json"),
]

results = {}

for term, outfile in SEARCHES:
    print(f"Searching CA SOS: {term}...")
    url = f"https://businesssearch.sos.ca.gov/api?searchTerm={term.replace(' ', '+')}&entityType=LP+LLC+Corporation&status=Active"
    try:
        r = subprocess.run(
            ["curl", "-s", "-L", "--max-time", "15", url],
            capture_output=True, text=True, timeout=20
        )
        data = json.loads(r.stdout) if r.stdout.strip().startswith("{") else {}
        results[term] = data
        with open(WORK_DIR / outfile, "w") as f:
            json.dump(data, f, indent=2)
        # Extract businesses
        businesses = data.get("businesses", []) if isinstance(data, dict) else []
        print(f"  -> {len(businesses)} results")
        for b in businesses:
            print(f"     {b.get('l1', '?')} | {b.get('l2', '?')} | {b.get('l3', '?')} | {b.get('l4', '?')} | {b.get('l5', '?')}")
    except Exception as e:
        print(f"  ERROR: {e}")
        results[term] = {"error": str(e)}

# Also check NPPES for Mercy House licensed facilities
print("\n=== NPPES: Mercy House facilities with taxonomy ===")
try:
    from google.cloud import bigquery
    client = bigquery.Client(project="noble-beanbag-497411-m4")
    q = """
        SELECT org_name, city, taxonomy, npi
        FROM `noble-beanbag-497411-m4.nppes_export.oc_lb_orgs`
        WHERE UPPER(org_name) LIKE '%MERCY%'
           OR UPPER(org_name) LIKE '%HOUSING%'
           OR UPPER(org_name) LIKE '%CHDO%'
           OR UPPER(org_name) LIKE '%VAGABOND%'
           OR UPPER(org_name) LIKE '%CAS A%'
        LIMIT 50
    """
    df = client.query(q).to_dataframe()
    df.to_csv(WORK_DIR / "nppes_mercy_facilities.csv", index=False)
    print(f"  Found {len(df)} NPPES entries")
    print(df[["org_name", "city", "taxonomy"]].to_string())
except Exception as e:
    print(f"  NPPES error: {e}")

# Also search PPP for additional Mercy-related entities in CA
print("\n=== PPP: Mercy House + CA entities ===")
try:
    from google.cloud import bigquery
    client = bigquery.Client(project="noble-beanbag-497411-m4")
    q = """
        SELECT BorrowerName, BorrowerAddress, BorrowerCity, BorrowerState,
               InitialApprovalAmount, LoanStatus, LoanNumber
        FROM `noble-beanbag-497411-m4.ppp_rico.ppp_150k_plus`
        WHERE UPPER(BorrowerName) LIKE '%MERCY%'
           AND UPPER(BorrowerState) = 'CA'
        LIMIT 50
    """
    df = client.query(q).to_dataframe()
    df.to_csv(WORK_DIR / "ppp_mercy_ca.csv", index=False)
    print(f"  Found {len(df)} CA Mercy PPP loans")
    print(df[["BorrowerName", "BorrowerCity", "InitialApprovalAmount", "LoanStatus"]].to_string())
except Exception as e:
    print(f"  PPP error: {e}")

print("\nDone. Files saved to opencode_work.")
