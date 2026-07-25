import os
import io
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

TOKEN_FILE = r"C:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\token.json"
# Try fallback token if needed
if not os.path.exists(TOKEN_FILE):
    TOKEN_FILE = r"C:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\token_drive_upload.json"

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

def main():
    if not os.path.exists(TOKEN_FILE):
        print(f"[ERROR] Token file not found at: {TOKEN_FILE}")
        return
        
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    service = build("drive", "v3", credentials=creds)
    
    print("[*] Searching Google Drive for 'OSINT-NeoAI-Manus-Export.tar.gz'...")
    query = "name = 'OSINT-NeoAI-Manus-Export.tar.gz' and trashed = false"
    results = service.files().list(
        q=query,
        fields="files(id, name, mimeType, size)",
        includeItemsFromAllDrives=True,
        supportsAllDrives=True
    ).execute()
    
    files = results.get("files", [])
    if not files:
        print("[!] No matching file found on Google Drive.")
        return
        
    file_info = files[0]
    file_id = file_info["id"]
    file_name = file_info["name"]
    print(f"[+] Found file: {file_name} (ID: {file_id}, Size: {file_info.get('size')} bytes)")
    
    dest_dir = r"C:\Users\HP\OneDrive\Documents\opencode_work"
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, file_name)
    
    print(f"[*] Downloading to: {dest_path}...")
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(f"    Download Progress: {int(status.progress() * 100)}%")
        
    fh.seek(0)
    with open(dest_path, "wb") as f:
        f.write(fh.read())
        
    print(f"[SUCCESS] Download completed! File saved at: {dest_path}")

if __name__ == "__main__":
    main()
