"""
live_drive_search.py — Direct keyword search against Google Drive API (no BigQuery needed)
"""
import os, sys
sys.stdout.reconfigure(encoding="utf-8")

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE   = os.path.join(SCRIPT_DIR, "token.json")
SECRET_FILE  = os.path.join(SCRIPT_DIR, "client_secret.json")
SCOPES       = ["https://www.googleapis.com/auth/drive.readonly"]

KEYWORDS = [
    "HBNC",
    "navigation center",
    "211",
    "hexavalent",
    "arsenic",
    "chromium",
    "CEQA",
    "RPM Modular",
    "Cameron Lane",
    "contamination",
    "CARES",
    "Newsom",
    "HHAP",
    "HMIS",
    "qui tam",
    "RICO",
    "toxic",
    "Stanford",
]

def get_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return build("drive", "v3", credentials=creds)

def search_keyword(service, keyword):
    query = f"fullText contains '{keyword}' and trashed=false"
    results = service.files().list(
        q=query,
        pageSize=20,
        fields="files(id, name, mimeType, modifiedTime, webViewLink)",
        includeItemsFromAllDrives=True,
        supportsAllDrives=True
    ).execute()
    return results.get("files", [])

def main():
    print("=" * 65)
    print("  LIVE GOOGLE DRIVE KEYWORD SEARCH")
    print("=" * 65)

    service = get_service()
    all_hits = {}

    for kw in KEYWORDS:
        hits = search_keyword(service, kw)
        if hits:
            all_hits[kw] = hits
            print(f"\n[+] '{kw}' — {len(hits)} file(s) found:")
            for f in hits:
                print(f"    • {f['name']}")
                print(f"      Type: {f['mimeType']} | Modified: {f['modifiedTime']}")
                print(f"      Link: {f.get('webViewLink','N/A')}")
        else:
            print(f"[ ] '{kw}' — no matches")

    print("\n" + "=" * 65)
    print(f"  SUMMARY: {len(all_hits)} keywords returned results")
    total_files = sum(len(v) for v in all_hits.values())
    print(f"  TOTAL FILE HITS: {total_files}")
    print("=" * 65)

if __name__ == "__main__":
    main()
