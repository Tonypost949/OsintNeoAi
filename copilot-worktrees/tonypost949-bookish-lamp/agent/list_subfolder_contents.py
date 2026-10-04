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
    
    # 1. Find the parent folder 'G_Drive_Backup_20260622' ID
    results = service.files().list(
        q="name='G_Drive_Backup_20260622' and mimeType='application/vnd.google-apps.folder' and trashed=false",
        fields="files(id, name)"
    ).execute()
    
    items = results.get('files', [])
    if not items:
        print("Folder 'G_Drive_Backup_20260622' not found in Drive.")
        return
    parent_id = items[0]['id']
    
    # 2. Find '619onedrivepost' folder ID under parent
    results2 = service.files().list(
        q=f"name='619onedrivepost' and mimeType='application/vnd.google-apps.folder' and '{parent_id}' in parents and trashed=false",
        fields="files(id, name)"
    ).execute()
    
    items2 = results2.get('files', [])
    if not items2:
        print("Folder '619onedrivepost' not found under parent in Drive.")
        return
    folder_id = items2[0]['id']
    print(f"Listing files in folder '619onedrivepost' on Google Drive (ID: {folder_id})...\n")
    
    # 3. List files in this folder
    query = f"'{folder_id}' in parents and trashed = false"
    files_results = service.files().list(
        q=query,
        fields="files(id, name, size, mimeType)"
    ).execute()
    
    files = files_results.get('files', [])
    if not files:
        print("No files found in '619onedrivepost' on Drive.")
        return
        
    for f in files:
        size_bytes = int(f.get('size', 0)) if 'size' in f else 0
        size_mb = size_bytes / 1024**2
        print(f"- {f['name']} ({size_mb:.2f} MB, Type: {f['mimeType']})")

if __name__ == "__main__":
    main()
