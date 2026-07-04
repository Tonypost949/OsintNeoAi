import os
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
    
    # Find the G_Drive_Backup_20260622 folder ID
    results = service.files().list(
        q="name='G_Drive_Backup_20260622' and mimeType='application/vnd.google-apps.folder' and trashed=false",
        fields="files(id, name)"
    ).execute()
    
    items = results.get('files', [])
    if not items:
        print("Folder 'G_Drive_Backup_20260622' not found in Drive.")
        return
        
    folder_id = items[0]['id']
    print(f"Listing files in folder 'G_Drive_Backup_20260622' (ID: {folder_id})...\n")
    
    # List files in this folder
    query = f"'{folder_id}' in parents and trashed = false"
    files_results = service.files().list(
        q=query,
        fields="files(id, name, size, mimeType)"
    ).execute()
    
    files = files_results.get('files', [])
    if not files:
        print("No files found in this folder.")
        return
        
    for f in files:
        size_bytes = int(f.get('size', 0)) if 'size' in f else 0
        size_mb = size_bytes / 1024**2
        print(f"- {f['name']} ({size_mb:.2f} MB, Type: {f['mimeType']})")

if __name__ == "__main__":
    main()
