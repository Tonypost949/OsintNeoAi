import urllib.request
import json
import ssl

def search_ca_controller_mirror():
    # We will search the CA Open Data Portal (data.ca.gov) or public dataset mirrors
    # Let's search the data.ca.gov CKAN API for unclaimed property datasets
    print("Querying California Open Data Portal (data.ca.gov) CKAN API...")
    url = "https://data.ca.gov/api/3/action/package_search?q=unclaimed+property"
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, context=ctx, timeout=10)
        data = json.loads(res.read().decode('utf-8'))
        results = data.get("result", {}).get("results", [])
        print(f"Found {len(results)} matching datasets on data.ca.gov:")
        for r in results:
            print(f"- Title: {r.get('title')}")
            for res_file in r.get("resources", []):
                print(f"  - Resource: {res_file.get('name')} | URL: {res_file.get('url')}")
    except Exception as e:
        print(f"Error querying data.ca.gov: {e}")

search_ca_controller_mirror()
