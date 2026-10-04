"""
monitor_lightbox_gateway.py — Background Gateway Sync & Ingestion Monitor
==========================================================================
Monitors the LightBox RE API key propagation and executes automated 
parcel searches as soon as the edge gateway activates.
"""

import os
import sys
import time
import json
import requests

KEY = "H81DuBbxyMlfmKIGzVeQ8L7vbUG56x3xwS6yorMK5R5trpUc"
headers = {
    "x-api-key": KEY,
    "Accept": "application/json",
    "Content-Type": "application/json"
}

target_addresses = [
    "17642 Beach Blvd, Huntington Beach, CA 92647",
    "17631 Cameron Ln, Huntington Beach, CA 92647",
    "19102 Beach Blvd, Huntington Beach, CA 92648"
]

def check_gateway():
    url = f"https://api.lightboxre.com/v1/parcels/us/address?text=17642%20Beach%20Blvd,%20Huntington%20Beach,%20CA"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        return r.status_code, r.text
    except Exception as e:
        return 0, str(e)

print("=== STARTING LIGHTBOX RE API GATEWAY MONITOR ===")
print(f"Monitoring Consumer Key: {KEY[:8]}...")

status, body = check_gateway()
print(f"Initial Check: Status {status}")

if status == 200:
    print("✨ Gateway Active! Executing Target Searches...")
    for addr in target_addresses:
        print(f"\nQuerying: '{addr}'...")
        r = requests.get("https://api.lightboxre.com/v1/parcels/us/address", headers=headers, params={"text": addr})
        if r.status_code == 200:
            data = r.json()
            out_file = f"lightbox_parcel_{addr.split(',')[0].replace(' ', '_')}.json"
            with open(out_file, "w") as f:
                json.dump(data, f, indent=2)
            print(f"Saved: {out_file}")
else:
    print(f"Gateway Response: {body[:150]}")
    print("Standing by for edge gateway propagation...")
