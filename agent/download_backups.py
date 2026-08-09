import os
import io
import logging
from pathlib import Path

# Google client libraries
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SOURCE_DIR = r"C:\Users\HP\.gemini\antigravity-ide\brain\c370d570-1fbc-427b-a511-94af4ff83ad7"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token_drive_upload.json")
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def get_drive_service():
    if not os.path.exists(TOKEN_FILE):
        raise FileNotFoundError("Missing token_drive_upload.json. Please run backup script first or authorize.")
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    return build("drive", "v3", credentials=creds)

def main():
    logging.info("Starting restore from Google Drive...")
    drive = get_drive_service()
    
    # 1. Find the OSINT_PC_Backups folder ID
    results = drive.files().list(
        q="name='OSINT_PC_Backups' and mimeType='application/vnd.google-apps.folder' and trashed=false",
        spaces='drive',
        fields="files(id, name)"
    ).execute()
    
    folders = results.get('files', [])
    if not folders:
        logging.error("OSINT_PC_Backups folder not found in Google Drive.")
        return
        
    folder_id = folders[0]['id']
    logging.info(f"Found OSINT_PC_Backups folder ID: {folder_id}")
    
    # 2. List all files in the folder (with pagination)
    files = []
    page_token = None
    while True:
        results = drive.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            spaces='drive',
            fields="nextPageToken, files(id, name, mimeType)",
            pageToken=page_token,
            pageSize=1000
        ).execute()
        files.extend(results.get('files', []))
        page_token = results.get('nextPageToken', None)
        if not page_token:
            break
            
    # Filter to only download relevant MD files, csv, zip, and images to prevent cluttering
    valid_extensions = ('.md', '.jpg', '.png', '.img', '.zip', '.csv', '.xlsx', '.pdf')
    filtered_files = [f for f in files if f['name'].lower().endswith(valid_extensions)]
    logging.info(f"Total files in Drive: {len(files)}. Relevant files to download: {len(filtered_files)}")
    files = filtered_files
    
    # 3. Download each file
    os.makedirs(SOURCE_DIR, exist_ok=True)
    for f in files:
        file_id = f['id']
        file_name = f['name']
        mime_type = f['mimeType']
        
        # Skip folders if any nested folders exist
        if mime_type == 'application/vnd.google-apps.folder':
            continue
            
        dest_path = os.path.join(SOURCE_DIR, file_name)
        
        # Make sure parent directory exists (for system logs / messages folder)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        # Only download if file does not exist locally
        if os.path.exists(dest_path):
            logging.info(f"File already exists locally, skipping: {file_name}")
            continue
            
        logging.info(f"Downloading {file_name}...")
        try:
            request = drive.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                
            with open(dest_path, 'wb') as local_file:
                local_file.write(fh.getvalue())
            logging.info(f"✅ Successfully downloaded {file_name}")
        except Exception as e:
            logging.error(f"❌ Failed to download {file_name}: {e}")

if __name__ == "__main__":
    main()
