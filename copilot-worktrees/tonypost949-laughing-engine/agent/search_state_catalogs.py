import urllib.request
import json
import ssl

def search_state_catalogs():
    # We query the Socrata discovery API to search for "unclaimed property" datasets
    domains = {
        "texas": "https://api.us.socrata.com/api/catalog/v1?domains=data.texas.gov&q=unclaimed%20property",
        "new_york": "https://api.us.socrata.com/api/catalog/v1?domains=data.ny.gov&q=unclaimed%20property"
    }
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    headers = {"User-Agent": "Mozilla/5.0"}
    
    for state, search_url in domains.items():
        print(f"\n=== SEARCHING CATALOG FOR STATE: {state.upper()} ===")
        try:
            req = urllib.request.Request(search_url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
                data = json.loads(response.read().decode('utf-8'))
                results = data.get("results", [])
                print(f"Found {len(results)} matching datasets:")
                for r in results:
                    resource = r.get("resource", {})
                    print(f" - Title: {resource.get('name')}")
                    print(f"   ID: {resource.get('id')}")
                    print(f"   Description: {resource.get('description', '')[:100]}...")
                    # We can use the first active dataset ID found
        except Exception as e:
            print(f"Error searching {state}: {e}")

if __name__ == "__main__":
    search_state_catalogs()
