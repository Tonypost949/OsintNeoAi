import os
import sys
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

sys.stdout.reconfigure(encoding="utf-8")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token.json")
if not os.path.exists(TOKEN_FILE) and os.path.exists(os.path.join(SCRIPT_DIR, "token_drive_upload.json")):
    TOKEN_FILE = os.path.join(SCRIPT_DIR, "token_drive_upload.json")

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

def get_drive_service():
    if not os.path.exists(TOKEN_FILE):
        return None
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build("drive", "v3", credentials=creds)

def download_specific_files():
    service = get_drive_service()
    if not service:
        print("[ERROR] Service not available")
        return
        
    target_names = [
        "RESIDENTS OF MERCY HOUSE NAVIGATION CENTER",
        "TruthFinder Reports for Property Residents",
        "truthfinder_scan_results.json"
    ]
    
    for name in target_names:
        print(f"\n--- Searching for: {name} ---")
        try:
            results = service.files().list(
                q=f"name = '{name}' and trashed=false",
                fields="files(id, name, mimeType)",
                includeItemsFromAllDrives=True,
                supportsAllDrives=True
            ).execute()
            files = results.get("files", [])
            if not files:
                # Try contains instead
                results = service.files().list(
                    q=f"name contains '{name}' and trashed=false",
                    fields="files(id, name, mimeType)",
                    includeItemsFromAllDrives=True,
                    supportsAllDrives=True
                ).execute()
                files = results.get("files", [])
                
            if not files:
                print(f"File not found: {name}")
                continue
                
            for f in files:
                fid = f["id"]
                fname = f["name"]
                mime = f["mimeType"]
                print(f"Found file: {fname} (ID: {fid}, Type: {mime})")
                
                # Download and print content
                if "google-apps.document" in mime:
                    content = service.files().export(fileId=fid, mimeType="text/plain").execute().decode('utf-8', errors='ignore')
                else:
                    content = service.files().get_media(fileId=fid).execute().decode('utf-8', errors='ignore')
                
                # Print first 2000 chars of the content
                print("Content preview:")
                print(content[:3000])
                print("..." if len(content) > 3000 else "")
                
                # Save locally for reference
                local_save = os.path.join(SCRIPT_DIR, f"downloaded_{fname.replace(' ', '_').replace('/', '_')}")
                if "json" in mime or fname.endswith(".json"):
                    if not local_save.endswith(".json"):
                        local_save += ".json"
                else:
                    if not local_save.endswith(".txt"):
                        local_save += ".txt"
                with open(local_save, "w", encoding="utf-8") as out:
                    out.write(content)
                print(f"Saved content to {local_save}")
                
        except Exception as e:
            print(f"Error downloading {name}: {e}")

if __name__ == "__main__":
    download_specific_files()
