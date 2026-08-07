import os
import sys
import logging
import zipfile
import datetime
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

sys.stdout.reconfigure(encoding="utf-8")

DRIVE_FOLDER_ID = "1q5bmZJQ9IuSudsie1KNuMWZ0mbfu6-gE" # "sharedall" folder ID
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRETS_FILE = os.path.join(SCRIPT_DIR, "client_secret.json")
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token_drive_upload.json")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def get_drive_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    elif os.path.exists(os.path.join(SCRIPT_DIR, "token.json")):
        creds = Credentials.from_authorized_user_file(os.path.join(SCRIPT_DIR, "token.json"), SCOPES)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logging.info("Refreshing credentials...")
            try:
                creds.refresh(Request())
            except Exception as e:
                logging.warning(f"Failed to refresh credentials: {e}. Re-authenticating...")
                creds = None
        
        if not creds:
            logging.info("Starting OAuth flow...")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w", encoding="utf-8") as token:
            token.write(creds.to_json())
    return build("drive", "v3", credentials=creds)

def zip_project(source_dir, output_filename):
    logging.info(f"Zipping project into {output_filename}...")
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            if '.git' in dirs:
                dirs.remove('.git')
            if '__pycache__' in dirs:
                dirs.remove('__pycache__')
            if 'venv' in dirs:
                dirs.remove('venv')
            for file in files:
                # Do not zip the zip file itself or other huge zip files
                if file == os.path.basename(output_filename) or file.endswith('.zip'):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, start=source_dir)
                zipf.write(file_path, arcname)
    logging.info("Zip creation complete.")

def upload_file(service, filepath_str, folder_id):
    file_name = os.path.basename(filepath_str)
    file_metadata = {
        "name": file_name,
        "parents": [folder_id]
    }
    media = MediaFileUpload(filepath_str, resumable=True)
    request = service.files().create(body=file_metadata, media_body=media, fields="id")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            logging.info(f"Uploading {file_name} - {int(status.progress() * 100)}% complete")
    return response.get("id")

def main():
    logging.info("=== Archiving OSINT-AGENT to Google Drive sharedall ===")
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"osint_agent_backup_{timestamp}.zip"
    zip_filepath = os.path.join(SCRIPT_DIR, zip_filename)
    
    try:
        zip_project(SCRIPT_DIR, zip_filepath)
        service = get_drive_service()
        
        logging.info(f"Uploading new backup: {zip_filename}")
        file_id = upload_file(service, zip_filepath, DRIVE_FOLDER_ID)
        logging.info(f"Successfully uploaded: {zip_filename} (Drive ID: {file_id})")
        
        # Cleanup local zip after upload
        os.remove(zip_filepath)
        logging.info(f"Cleaned up local zip file {zip_filename}.")
        
    except Exception as e:
        import traceback
        logging.error(f"Sync process failed: {e}")
        traceback.print_exc()
        if os.path.exists(zip_filepath):
            os.remove(zip_filepath)
            
    logging.info("=== Sync completed ===")

if __name__ == "__main__":
    main()
