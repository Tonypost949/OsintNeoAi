import os
import logging
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

SCRATCH_DIR = r"G:\AG2_Backups"
ZIPS_TO_BACKUP = [
    "OSINT_VAULT_BACKUP.zip",
    "OPENCODE_BACKUP.zip",
    "OSINTNeoAiCLI.zip",
    "OSINTtimeAi.zip",
    "osint-agent.zip"
]

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRETS_FILE = os.path.join(SCRIPT_DIR, "client_secret.json")
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token_drive_upload.json")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def get_drive_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w", encoding="utf-8") as token:
            token.write(creds.to_json())
    return build("drive", "v3", credentials=creds)

def ensure_folder_exists(service, folder_name="sharedall"):
    """Look for a folder named sharedall, if not create it."""
    results = service.files().list(
        q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
        spaces='drive',
        fields="files(id, name)"
    ).execute()
    items = results.get('files', [])
    if not items:
        logging.info(f"Creating '{folder_name}' folder in Google Drive...")
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')
    return items[0].get('id')

def main():
    logging.info("=== Starting Scratch Zips Backup ===")
    try:
        service = get_drive_service()
        folder_id = ensure_folder_exists(service, "sharedall")
        logging.info(f"Destination Folder ID: {folder_id}")

        for zip_name in ZIPS_TO_BACKUP:
            file_path = os.path.join(SCRATCH_DIR, zip_name)
            if os.path.exists(file_path):
                logging.info(f"Uploading {zip_name} to Google Drive...")
                file_metadata = {
                    "name": zip_name,
                    "parents": [folder_id],
                }
                media = MediaFileUpload(file_path, resumable=True)
                request = service.files().create(body=file_metadata, media_body=media, fields="id")
                response = None
                while response is None:
                    status, response = request.next_chunk()
                    if status:
                        logging.info(f"Upload progress for {zip_name}: {status.progress() * 100:.1f}%")
                
                # Verify we got a valid response (uploaded successfully) before deleting
                if response and response.get('id'):
                    logging.info(f"Uploaded {zip_name} successfully. Drive ID: {response.get('id')}")
                    try:
                        # Delete local file to free space and stop OneDrive syncing it
                        os.remove(file_path)
                        logging.info(f"Deleted local file to save space: {file_path}")
                    except Exception as delete_error:
                        logging.error(f"Could not delete local file {zip_name} (it may be locked by another process/OneDrive): {delete_error}")
                else:
                    logging.error(f"Failed upload validation for {zip_name}. Local file kept.")
            else:
                logging.warning(f"File not found: {file_path}")

    except Exception as e:
        logging.error(f"Critical error in backup: {e}")

if __name__ == "__main__":
    main()
