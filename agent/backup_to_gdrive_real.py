import os
import io
import logging
from pathlib import Path

# Google client libraries
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

# ----------------------------------------------------------------------
# -------------------------- CONFIGURATION ----------------------------
# ----------------------------------------------------------------------
# 1. Folder on your PC you want to back up
SOURCE_DIR = r"C:\Users\HP\.gemini\antigravity-ide\brain\52e78ece-a12b-4269-b588-efb7b8d709c2"

# 2. Delete the local file after a successful upload? (True = move, False = copy)
DELETE_AFTER_UPLOAD = False

# 3. Scopes needed for Drive access
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

# 4. Filenames for credentials / token (kept alongside this script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRETS_FILE = os.path.join(SCRIPT_DIR, "client_secret.json")
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token_drive_upload.json")

# ----------------------------------------------------------------------
# -------------------------- LOGGING SETUP ----------------------------
# ----------------------------------------------------------------------
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
    """Authenticate and return a Drive service object."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If there are no (valid) credentials, run the OAuth flow.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(TOKEN_FILE, "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    return build("drive", "v3", credentials=creds)

def ensure_folder_exists(service, folder_name="OSINT_PC_Backups"):
    """Check if the backup folder exists in Drive, if not create it."""
    results = service.files().list(
        q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
        spaces='drive',
        fields="nextPageToken, files(id, name)"
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
    else:
        return items[0].get('id')

def list_files_to_backup(root):
    """Recursively collect all file paths under *root*."""
    files = []
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            files.append(Path(dirpath) / name)
    return files

def upload_file(service, local_path, folder_id):
    """
    Upload a single file to Google Drive.
    Returns the Drive file ID on success.
    """
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
    logging.info("=== Google Drive Backup Started ===")
    logging.info("Source directory: %s", SOURCE_DIR)

    if not os.path.isdir(SOURCE_DIR):
        logging.error("Source directory does not exist – aborting.")
        return

    try:
        drive = get_drive_service()
        folder_id = ensure_folder_exists(drive)
        logging.info("Destination Drive folder ID: %s", folder_id)
        
        files = list_files_to_backup(SOURCE_DIR)

        if not files:
            logging.info("No files found to backup – exiting.")
            return

        for f in files:
            try:
                logging.info("Uploading %s", f)
                file_id = upload_file(drive, f, folder_id)
                logging.info("✅ Uploaded %s → Drive ID %s", f, file_id)

                if DELETE_AFTER_UPLOAD:
                    f.unlink()  # delete the local file
                    logging.info("🗑️ Deleted local copy %s", f)

            except Exception as exc:
                logging.error("❌ Failed to process %s – %s", f, exc)

        logging.info("=== Backup job completed ===")
        
    except Exception as e:
        logging.error(f"Critical error in backup: {e}")

if __name__ == "__main__":
    main()
