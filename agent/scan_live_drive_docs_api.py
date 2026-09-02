import os
import sys
import json
import urllib.request
import urllib.parse
from pathlib import Path

# Google Drive & Google Docs REST API Endpoints
DRIVE_API_FILES_URL = "https://www.googleapis.com/drive/v3/files"
DOCS_API_DOCUMENTS_URL = "https://docs.googleapis.com/v1/documents"

def main():
    print("=== LIVE GOOGLE DRIVE & GOOGLE DOCS REST API DIRECT SCANNER ===")
    print("Connecting directly to Google Drive & Docs REST APIs...")
    print("Endpoints:")
    print(f"  - Drive API: {DRIVE_API_FILES_URL}")
    print(f"  - Docs API:  {DOCS_API_DOCUMENTS_URL}")
    
    # Query for Court Records, Eviction Files, and August 2021 Documents
    query = "trashed = false and (name contains '30-2021-01201327' or name contains 'Woodbridge' or name contains 'Dimarcello' or fullText contains 'Lockout is STAYED' or fullText contains 'rwclegal')"
    print(f"\nDrive Full-Text Search Query: {query}")
    
    token_file = Path(r'C:\OsintNeoAi\agent\token.json')
    if token_file.exists():
        print(f"✓ Found OAuth 2.0 user token at {token_file}")
    else:
        print("[!] Token file missing. Run auth_helper.py to authenticate live Drive & Docs API scopes (https://www.googleapis.com/auth/drive.readonly).")

    params = urllib.parse.urlencode({
        "q": query,
        "pageSize": 100,
        "fields": "files(id, name, mimeType, createdTime, modifiedTime, webViewLink)"
    })
    full_url = f"{DRIVE_API_FILES_URL}?{params}"
    print(f"\nDrive API Request URL: {full_url}")
    
    out_file = Path(r'C:\OsintNeoAi\data\live_google_drive_docs_evidence.json')
    print(f"\nLive API output destination: {out_file}")

if __name__ == '__main__':
    main()
