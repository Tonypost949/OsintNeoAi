import requests

base_url = "https://data.egovoc.com/db/data.php"

# Query t0 (Total Annual County Expenditures) for Program III (Infrastructure & Environmental)
print("[*] Querying Expenditures for Program III (Infrastructure & Environmental)...")
try:
    r = requests.get(f"{base_url}?ds=t0&prog=3", timeout=30)
    if r.status_code == 200:
        data = r.json()
        print(f"[+] Retrieved categories/years: {data.get('categories')}")
        print(f"[+] Series under Program III ({len(data.get('series', []))} entries):")
        for s in data.get('series', []):
            # Print series names and values
            data_points = ", ".join(f"${val:,.0f}" for val in s.get('data', []))
            print(f"  - {s.get('name')} (CID: {s.get('cid')}, CTY: {s.get('cty')}): {data_points}")
    else:
        print(f"[-] HTTP {r.status_code}")
except Exception as e:
    print(f"[-] Error: {e}")
