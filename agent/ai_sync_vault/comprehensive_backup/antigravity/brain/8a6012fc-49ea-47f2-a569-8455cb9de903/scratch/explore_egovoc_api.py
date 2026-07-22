import requests
import json

base_url = "https://data.egovoc.com/db/data.php"

# Let's query t4 (Revenues by department) to see what departments exist
print("[*] Querying t4 (Revenues by department) from OpenOC...")
try:
    r = requests.get(f"{base_url}?ds=t4", timeout=30)
    if r.status_code == 200:
        data = r.json()
        print(f"[+] Retrieved {len(data.get('series', []))} departments:")
        for s in data.get('series', [])[:20]:
            print(f"  - Name: {s.get('name')} | ID/CID: {s.get('cid')} | CTY: {s.get('cty')}")
    else:
        print(f"[-] HTTP {r.status_code}")
except Exception as e:
    print(f"[-] Error: {e}")
