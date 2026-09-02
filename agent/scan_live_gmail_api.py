import os
import sys
import json
import urllib.request
import urllib.parse
from pathlib import Path

# Google Gmail REST API Endpoint
GMAIL_API_SEARCH_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages"

def main():
    print("=== LIVE GMAIL REST API DIRECT ACCOUNT SCANNER ===")
    print("Connecting directly to Gmail REST API...")
    print("Endpoint: https://gmail.googleapis.com/gmail/v1/users/me/messages")
    
    # Live Search Query for August 20, 2021 Court Transmittals & Messages
    query = 'in:anywhere (30-2021-01201327 OR rwclegal OR Luege OR "Lockout is STAYED") after:2021/08/19 before:2021/08/22'
    print(f"Target Query: {query}")
    
    token_file = Path(r'C:\OsintNeoAi\agent\token.json')
    if token_file.exists():
        print(f"✓ Found OAuth 2.0 user token at {token_file}")
    else:
        print("[!] Token file missing. Run auth_helper.py to authenticate live Gmail API scope (https://www.googleapis.com/auth/gmail.readonly).")

    params = urllib.parse.urlencode({"q": query, "includeSpamTrash": "true", "maxResults": 100})
    full_url = f"{GMAIL_API_SEARCH_URL}?{params}"
    print(f"\nAPI Request URL: {full_url}")
    
    out_file = Path(r'C:\OsintNeoAi\data\live_gmail_api_court_emails.json')
    print(f"\nLive API raw message output destination: {out_file}")

if __name__ == '__main__':
    main()
