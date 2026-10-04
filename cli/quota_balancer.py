import json
import urllib.request
import urllib.error
import sys
import os

VAULT_PATH = r"C:\Amd949609_Antigravity_v1\Amd949609_keys\api_vault.json"

def check_key(api_key):
    if "PUT_" in api_key or not api_key.strip():
        return False
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash?key={api_key}"
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                return True
    except urllib.error.HTTPError as e:
        if e.code == 429: # Quota Exhausted
            return False
        return True # If it's a 400 Bad Request, the key is structurally valid, just a bad ping.
    except Exception:
        return False
    return False

def main():
    if not os.path.exists(VAULT_PATH):
        sys.exit(1)
        
    with open(VAULT_PATH, "r") as f:
        data = json.load(f)
        
    keys = data.get("google_pro_keys", [])
    
    for key in keys:
        if check_key(key):
            print(key)
            sys.exit(0)
            
    # If all fail or aren't set, print the first one as fallback
    if keys:
        print(keys[0])

if __name__ == "__main__":
    main()
