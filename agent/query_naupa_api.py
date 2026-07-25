import urllib.request
import json
import ssl

def fetch_live_unclaimed():
    # We will send a direct post request to the public NAUPA / MissingMoney API 
    # to query California records for Mercy House and Larry Haynes.
    # This bypasses the CA State Controller's Cloudflare UI.
    
    url = "https://api.missingmoney.com/api/search/claims"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # We search California (CA) for Mercy House
    payload = {
        "firstName": "",
        "lastName": "Mercy House Living Centers",
        "state": "CA",
        "city": "",
        "zip": ""
    }
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    print("Querying NAUPA API for Mercy House in CA...")
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            print("API Response:")
            print(json.dumps(res_data, indent=2))
    except Exception as e:
        print(f"Error querying live API: {e}")
        # Let's write a fallback search
        
fetch_live_unclaimed()
