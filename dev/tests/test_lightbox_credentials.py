import requests
import json

LIGHTBOX_KEY = "H81DuBbxyMlfmKIGzVeQ8L7vbUG56x3xwS6yorMK5R5trpUc"
BASE_URL = "https://api.lightboxre.com/v1"

headers = {
    "x-api-key": LIGHTBOX_KEY,
    "Accept": "application/json",
    "Content-Type": "application/json"
}

test_addresses = [
    "17642 Beach Blvd, Huntington Beach, CA 92647",
    "17631 Cameron Ln, Huntington Beach, CA 92647",
    "19102 Beach Blvd, Huntington Beach, CA 92648"
]

print("=== TESTING LIGHTBOX RE API LIVE CREDENTIALS ===")

for addr in test_addresses:
    print(f"\nQuerying: '{addr}'...")
    url = f"{BASE_URL}/parcels/us/address"
    params = {"text": addr}
    
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        print(f"Status Code: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print("Response Data (First 500 chars):")
            print(json.dumps(data, indent=2)[:500])
        else:
            print(f"Error Response: {resp.text[:300]}")
    except Exception as e:
        print(f"Connection Exception: {e}")
