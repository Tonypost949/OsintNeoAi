import os
import logging
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token_drive_upload.json")
CLIENT_SECRETS_FILE = os.path.join(SCRIPT_DIR, "client_secret.json")
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

def main():
    if not os.path.exists(TOKEN_FILE):
        print("Google Drive authentication token not found locally.")
        return
        
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    service = build("drive", "v3", credentials=creds)
    
    # 1. Find the 'sharedall' folder ID
    results = service.files().list(
        q="name='sharedall' and mimeType='application/vnd.google-apps.folder' and trashed=false",
        fields="files(id, name)"
    ).execute()
    
    items = results.get('files', [])
    if not items:
        print("Folder 'sharedall' not found in Drive.")
        return
        
    folder_id = items[0]['id']
    print(f"Checking Google Drive API for files in 'sharedall' (ID: {folder_id})...\n")
    
    # 2. List all files inside the folder, sorted by modifiedTime descending
    query = f"'{folder_id}' in parents and trashed = false"
    files_results = service.files().list(
        q=query,
        orderBy="modifiedTime desc",
        fields="files(id, name, size, modifiedTime)"
    ).execute()
    
    files = files_results.get('files', [])
    if not files:
        print("No files found in 'sharedall'.")
        return
        
    print(f"{'File Name':<50} | {'Size (MB)':<10} | {'Modified Time (UTC)'}")
    print("-" * 85)
    for f in files:
        size_bytes = int(f.get('size', 0))
        size_mb = size_bytes / 1024**2
        print(f"{f['name']:<50} | {size_mb:<10.2f} | {f['modifiedTime']}")

if __name__ == "__main__":
    main()
