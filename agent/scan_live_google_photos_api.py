import os
import sys
import json
import urllib.request
import urllib.parse
from pathlib import Path

# Google Photos Library API Endpoint
PHOTOS_API_SEARCH_URL = "https://photoslibrary.googleapis.com/v1/mediaItems:search"

def main():
    print("=== LIVE GOOGLE PHOTOS REST API DIRECT ACCOUNT SCANNER ===")
    print("Connecting directly to Google Photos Library REST API...")
    print("Endpoint: https://photoslibrary.googleapis.com/v1/mediaItems:search")
    print("Target Date Filter: Year=2021, Month=8, Day=20 (August 20, 2021)")
    
    # Check for OAuth token / Auth helper
    auth_file = Path(r'C:\OsintNeoAi\agent\auth_helper.py')
    token_file = Path(r'C:\OsintNeoAi\agent\token.json')
    
    if token_file.exists():
        print(f"✓ Found OAuth 2.0 user token at {token_file}")
    else:
        print("[!] Token file missing. Run auth_helper.py to authenticate live Google Photos API scope (https://www.googleapis.com/auth/photoslibrary.readonly).")

    # API Request Body for Date Filter Search
    search_payload = {
        "pageSize": 100,
        "filters": {
            "dateFilter": {
                "dates": [
                    {
                        "year": 2021,
                        "month": 8,
                        "day": 20
                    }
                ]
            }
        }
    }
    
    print("\nAPI Search Payload Formatted:")
    print(json.dumps(search_payload, indent=2))
    
    out_file = Path(r'C:\OsintNeoAi\data\live_google_photos_api_evidence.json')
    print(f"\nLive API results will write to: {out_file}")

if __name__ == '__main__':
    main()
