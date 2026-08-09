import os
import sys
import zipfile
import logging
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Directory setups
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token_drive_upload.json")
CLIENT_SECRETS_FILE = os.path.join(SCRIPT_DIR, "client_secret.json")
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
TARGET_FOLDER = "sharedall"

SRC_DIR = r"C:\Users\HP\OneDrive\Documents\OsintNeoAi"
BACKUP_DIR = r"C:\Users\HP\OneDrive\Documents\opencode_work_backup"
os.makedirs(BACKUP_DIR, exist_ok=True)
ts = datetime.now().strftime("%Y%m%d_%H%M%S")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def get_drive_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_FILE, 'w') as f:
                f.write(creds.to_json())
        else:
            raise Exception("Google Drive authorization token not found or invalid.")
    return build("drive", "v3", credentials=creds)

def main():
    if not os.path.exists(SRC_DIR):
        logging.error(f"Source folder does not exist: {SRC_DIR}")
        return
        
    logging.info("Authenticating with Google Drive...")
    drive = get_drive_service()
    
    # Find sharedall folder
    logging.info(f"Looking for '{TARGET_FOLDER}' folder in Drive...")
    results = drive.files().list(
        q=f"name='{TARGET_FOLDER}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
        spaces='drive', fields="files(id, name)").execute()
    items = results.get('files', [])
    if items:
        folder_id = items[0]['id']
        logging.info(f"Found {TARGET_FOLDER} (ID: {folder_id})")
    else:
        logging.info(f"Creating {TARGET_FOLDER} folder...")
        folder_id = drive.files().create(
            body={'name': TARGET_FOLDER, 'mimeType': 'application/vnd.google-apps.folder'},
            fields='id').execute()['id']

    # Zip the folder
    zip_path = os.path.join(BACKUP_DIR, f"osintneoai_FULL_{ts}.zip")
    logging.info(f"Zipping {SRC_DIR} to {zip_path}...")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(SRC_DIR):
            # Exclude standard heavy/temporary dirs
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.vscode', 'venv']]
            for f in files:
                fp = os.path.join(root, f)
                arcname = os.path.relpath(fp, SRC_DIR)
                try:
                    zf.write(fp, arcname)
                except Exception as e:
                    logging.warning(f"Could not write {f}: {e}")
                    
    sz = os.path.getsize(zip_path) / 1024**2
    logging.info(f"Zip completed successfully! Size: {sz:.2f} MB")
    
    # Upload to Google Drive
    logging.info("Uploading OsintNeoAi backup to Google Drive...")
    media = MediaFileUpload(zip_path, resumable=True)
    file_metadata = {
        'name': os.path.basename(zip_path),
        'parents': [folder_id]
    }
    
    request = drive.files().create(body=file_metadata, media_body=media, fields="id")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            logging.info(f"Upload progress: {int(status.progress() * 100)}% complete")
            
    if response and response.get('id'):
        logging.info(f"✅ Successfully uploaded to Drive! Drive ID: {response.get('id')}")
        print(f"\nSuccessfully backed up {os.path.basename(zip_path)} ({sz:.2f} MB)")
    else:
        logging.error("❌ Failed to get a valid response from Drive upload.")

if __name__ == "__main__":
    main()
