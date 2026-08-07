import os
import sys
import logging
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

# Configure stdout for utf-8
sys.stdout.reconfigure(encoding="utf-8")

# ----------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------
SOURCE_DIR = r"C:\Users\HP\Downloads"
DRIVE_FOLDER_ID = "1q5bmZJQ9IuSudsie1KNuMWZ0mbfu6-gE" # "sharedall" folder ID
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRETS_FILE = os.path.join(SCRIPT_DIR, "client_secret.json")
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token_drive_upload.json")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def get_drive_service():
    creds = None
    # Try loading from token_drive_upload.json first
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    elif os.path.exists(os.path.join(SCRIPT_DIR, "token.json")):
        creds = Credentials.from_authorized_user_file(os.path.join(SCRIPT_DIR, "token.json"), SCOPES)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logging.info("Refreshing credentials...")
            creds.refresh(Request())
        else:
            logging.info("Starting OAuth flow...")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w", encoding="utf-8") as token:
            token.write(creds.to_json())
    return build("drive", "v3", credentials=creds)

def list_local_files(directory):
    file_list = []
    for dirpath, _, filenames in os.walk(directory):
        # Skip 'report' directory inside downloads if we want, or include it.
        # Let's include everything
        for f in filenames:
            file_list.append(Path(dirpath) / f)
    return file_list

def file_exists_in_drive(service, name, folder_id):
    safe_name = name.replace("'", "\\'")
    query = f"name = '{safe_name}' and '{folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, fields="files(id)").execute()
    return len(results.get("files", [])) > 0

def upload_file(service, filepath, folder_id):
    file_metadata = {
        "name": filepath.name,
        "parents": [folder_id]
    }
    media = MediaFileUpload(str(filepath), resumable=True)
    request = service.files().create(body=file_metadata, media_body=media, fields="id")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            logging.info(f"Uploading {filepath.name} - {int(status.progress() * 100)}% complete")
    return response.get("id")

def main():
    logging.info("=== Scanning Downloads folder and Syncing to Google Drive ===")
    
    if not os.path.exists(SOURCE_DIR):
        logging.error(f"Source directory {SOURCE_DIR} does not exist.")
        return
        
    service = get_drive_service()
    local_files = list_local_files(SOURCE_DIR)
    
    logging.info(f"Found {len(local_files)} files in Downloads directory.")
    uploaded_count = 0
    
    for filepath in local_files:
        try:
            # Check if already exists in target folder to avoid duplicates
            if file_exists_in_drive(service, filepath.name, DRIVE_FOLDER_ID):
                logging.info(f"Skipped (already exists): {filepath.name}")
                continue
                
            logging.info(f"Uploading new file: {filepath.name}")
            file_id = upload_file(service, filepath, DRIVE_FOLDER_ID)
            logging.info(f"Successfully uploaded: {filepath.name} (Drive ID: {file_id})")
            uploaded_count += 1
        except Exception as e:
            logging.error(f"Failed to upload {filepath.name}: {e}")
            
    logging.info(f"=== Upload completed. {uploaded_count} new files uploaded to sharedall folder ===")
    
if __name__ == "__main__":
    main()
