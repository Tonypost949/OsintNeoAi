import os
import io
import logging
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

SOURCE_DIR = r"C:\Users\HP\OneDrive\Documents\opencode_work_backup"
DELETE_AFTER_UPLOAD = False
TARGET_FOLDER = "sharedall"
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

SCRIPT_DIR = r"C:\Users\HP\OneDrive\Documents\opencode_work\OSINT_VAULT_BACKUP"
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token_drive_upload.json")
CLIENT_SECRETS_FILE = os.path.join(SCRIPT_DIR, "client_secret.json")

log_file = os.path.join(SCRIPT_DIR, "backup_to_gdrive.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

def get_drive_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logging.info("Token expired, refreshing...")
            creds.refresh(Request())
        else:
            logging.info("No valid token, running OAuth flow...")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    return build("drive", "v3", credentials=creds)

def find_or_create_folder(service, folder_name):
    results = service.files().list(
        q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
        spaces='drive',
        fields="nextPageToken, files(id, name)"
    ).execute()

    items = results.get('files', [])
    if not items:
        logging.info(f"Creating '{folder_name}' folder in Google Drive...")
        file_metadata = {'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder'}
        folder = service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')
    else:
        logging.info(f"Found existing folder '{folder_name}' with ID: {items[0].get('id')}")
        return items[0].get('id')

def upload_file(service, local_path, folder_id):
    file_metadata = {
        "name": local_path.name,
        "parents": [folder_id],
    }
    media = MediaFileUpload(str(local_path), resumable=True)
    request = service.files().create(body=file_metadata, media_body=media, fields="id")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            logging.info("Uploading %s – %.2f%% complete", local_path.name, status.progress() * 100)
    return response.get("id")

def main():
    logging.info("=== opencode_work Backup to sharedall Started ===")
    logging.info("Source: %s", SOURCE_DIR)

    if not os.path.isdir(SOURCE_DIR):
        logging.error("Source directory does not exist – aborting.")
        return

    try:
        drive = get_drive_service()
        folder_id = find_or_create_folder(drive, TARGET_FOLDER)
        logging.info("Destination Drive folder ID: %s", folder_id)

        for f in Path(SOURCE_DIR).iterdir():
            if not f.is_file():
                continue
            try:
                logging.info("Uploading %s", f)
                file_id = upload_file(drive, f, folder_id)
                logging.info("Uploaded %s → Drive ID %s", f, file_id)
            except Exception as exc:
                logging.error("Failed to upload %s – %s", f, exc)

        logging.info("=== Backup job completed ===")

    except Exception as e:
        logging.error(f"Critical error: {e}")

if __name__ == "__main__":
    main()