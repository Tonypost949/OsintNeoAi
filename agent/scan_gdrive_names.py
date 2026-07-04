import os
import sys
import json
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

sys.stdout.reconfigure(encoding="utf-8")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token.json")
# We can also try token_drive_upload.json if token.json is not sufficient
if not os.path.exists(TOKEN_FILE) and os.path.exists(os.path.join(SCRIPT_DIR, "token_drive_upload.json")):
    TOKEN_FILE = os.path.join(SCRIPT_DIR, "token_drive_upload.json")

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive"
]

def get_drive_service():
    if not os.path.exists(TOKEN_FILE):
        print(f"[ERROR] Token file not found at {TOKEN_FILE}")
        return None
    try:
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        return build("drive", "v3", credentials=creds)
    except Exception as e:
        print(f"[ERROR] Auth failed: {e}")
        return None

def search_drive():
    service = get_drive_service()
    if not service:
        return
        
    print("[GDRIVE] Searching Google Drive for target files...")
    # Search queries for relevant filenames or content
    queries = [
        "name contains 'truthfinder'",
        "name contains 'resident'",
        "name contains 'homeless'",
        "name contains 'cameron'",
        "name contains 'beach'",
        "fullText contains 'truthfinder'",
        "fullText contains '17642'",
        "fullText contains '17631'"
    ]
    
    found_files = {}
    for q in queries:
        try:
            results = service.files().list(
                q=f"{q} and trashed=false",
                pageSize=100,
                fields="files(id, name, mimeType, size, webViewLink, parents)",
                includeItemsFromAllDrives=True,
                supportsAllDrives=True
            ).execute()
            files = results.get("files", [])
            for f in files:
                found_files[f["id"]] = f
        except Exception as e:
            print(f"[ERROR] Query '{q}' failed: {e}")
            
    print(f"[GDRIVE] Found {len(found_files)} unique files related to query keywords.")
    
    gdrive_matches = []
    # Let's inspect and download the content of text-like files to scan for names
    for fid, f in found_files.items():
        mime = f["mimeType"]
        fname = f["name"]
        print(f"Checking file: {fname} ({mime})")
        
        # Only download text/csv/markdown/json files or Google Docs
        if any(t in mime for t in ["text", "json", "csv", "markdown", "google-apps.document"]):
            try:
                if "google-apps.document" in mime:
                    # Export Google Doc as plain text
                    content = service.files().export(fileId=fid, mimeType="text/plain").execute().decode('utf-8', errors='ignore')
                else:
                    # Download media content
                    content = service.files().get_media(fileId=fid).execute().decode('utf-8', errors='ignore')
                
                # Scan for names and patterns in content
                lines = content.split('\n')
                for idx, line in enumerate(lines):
                    # Look for names/shelter/resident references
                    if any(kw in line.lower() for kw in ["shelter", "homeless", "resident", "occupant", "victim", "staying", "truthfinder", "dob", "ssn", "age"]):
                        context = lines[max(0, idx-5):min(len(lines), idx+15)]
                        gdrive_matches.append({
                            "file_id": fid,
                            "file_name": fname,
                            "line_num": idx + 1,
                            "text": line.strip(),
                            "context": "\n".join(context)
                        })
            except Exception as e:
                print(f"  [ERROR] Could not read content of {fname}: {e}")
                
    with open("gdrive_residents_scan.json", "w", encoding="utf-8") as out_f:
        json.dump(gdrive_matches, out_f, indent=2)
    print(f"[GDRIVE] Done! Found {len(gdrive_matches)} matches in Google Drive. Saved to gdrive_residents_scan.json")

if __name__ == "__main__":
    search_drive()
