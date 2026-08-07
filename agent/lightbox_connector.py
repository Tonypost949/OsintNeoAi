"""
lightbox_connector.py — LightBox RE API Master Integration Engine
==================================================================
Official API Documentation Base: https://lightbox.document360.io/docs/apis
Developer Portal: https://developer.lightboxre.com/apps/personal/lightbox/details

Supported Endpoints:
1. Parcels Search by Address: GET /v1/parcels/us/address
2. Parcels Search by APN:     GET /v1/parcels/us/{fips}/{apn}
3. Assessment Tax Data:       GET /v1/assessments/us/parcel/{parcel_id}
4. EDR Environmental Reports: GET /v1/edr/reports/address
5. Structure Geometry:        GET /v1/structures/us/parcel/{parcel_id}
"""

import os
import sys
import json
import requests

LIGHTBOX_API_KEY = os.environ.get("LIGHTBOX_API_KEY", "")
BASE_URL = "https://api.lightboxre.com/v1"

def get_headers():
    return {
        "x-api-key": LIGHTBOX_API_KEY,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

def search_parcel_by_address(address_text):
    """Search LightBox RE API by street address string."""
    if not LIGHTBOX_API_KEY:
        print("⚠️ LIGHTBOX_API_KEY not set. Set $env:LIGHTBOX_API_KEY='<YOUR_CONSUMER_KEY>'")
        return None

    url = f"{BASE_URL}/parcels/us/address"
    params = {"text": address_text}
    
    try:
        resp = requests.get(url, headers=get_headers(), params=params, timeout=15)
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"HTTP {resp.status_code}: {resp.text}")
            return None
    except Exception as e:
        print(f"Request error: {e}")
        return None

def fetch_edr_environmental_report(address_text):
    """Fetch EDR environmental radius report metadata for target site."""
    if not LIGHTBOX_API_KEY:
        print("⚠️ LIGHTBOX_API_KEY not set.")
        return None

    url = f"{BASE_URL}/edr/reports/address"
    params = {"text": address_text}
    
    try:
        resp = requests.get(url, headers=get_headers(), params=params, timeout=15)
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"HTTP {resp.status_code}: {resp.text}")
            return None
    except Exception as e:
        print(f"Request error: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query_addr = " ".join(sys.argv[1:])
        print(f"Executing LightBox API Search for: '{query_addr}'...")
        parcel_data = search_parcel_by_address(query_addr)
        if parcel_data:
            print(json.dumps(parcel_data, indent=2))
    else:
        print("LightBox RE API Engine Loaded. Ready to execute query upon receiving Consumer Key.")
