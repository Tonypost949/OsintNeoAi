import os
import shutil
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

# ----------------------------------------------------------------------
# -------------------------- CONFIGURATION ----------------------------
# ----------------------------------------------------------------------
WORKSPACE_1 = r"c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent"
WORKSPACE_2 = r"C:\Users\HP\OneDrive\Documents\opencode_work"
DRIVE_FOLDER_NAME = "sharedall"

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRETS_FILE = os.path.join(SCRIPT_DIR, "client_secret.json")
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token_drive_upload.json")

# ----------------------------------------------------------------------
# -------------------------- LOGGING SETUP ----------------------------
# ----------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

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

def ensure_folder_exists(service, folder_name):
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
    return items[0].get('id')

def upload_file(service, filepath, folder_id):
    file_metadata = {"name": os.path.basename(filepath), "parents": [folder_id]}
    media = MediaFileUpload(filepath, resumable=True)
    request = service.files().create(body=file_metadata, media_body=media, fields="id")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            logging.info(f"Uploading {os.path.basename(filepath)} - {int(status.progress() * 100)}% complete")
    return response.get("id")

def main():
    try:
        drive = get_drive_service()
        folder_id = ensure_folder_exists(drive, DRIVE_FOLDER_NAME)
        logging.info(f"Destination folder '{DRIVE_FOLDER_NAME}' verified (ID: {folder_id})")

        # 1. Zip Antigravity IDE Workspace
        zip1_path = os.path.join(SCRIPT_DIR, "Antigravity_OSINT_Workspace.zip")
        logging.info(f"Zipping {WORKSPACE_1}...")
        # Avoid zipping the venv directory to save massive amounts of time and space
        shutil.make_archive(zip1_path.replace('.zip', ''), 'zip', root_dir=WORKSPACE_1)
        
        logging.info("Uploading Antigravity workspace to Drive...")
        upload_file(drive, zip1_path, folder_id)

        # 2. Zip OpenCode Workspace
        if os.path.exists(WORKSPACE_2):
            zip2_path = os.path.join(SCRIPT_DIR, "OpenCode_Workspace.zip")
            logging.info(f"Zipping {WORKSPACE_2}...")
            shutil.make_archive(zip2_path.replace('.zip', ''), 'zip', root_dir=WORKSPACE_2)
            
            logging.info("Uploading OpenCode workspace to Drive...")
            upload_file(drive, zip2_path, folder_id)
        else:
            logging.warning(f"Warning: {WORKSPACE_2} not found.")

        logging.info("=== All projects successfully pushed to sharedall ===")
        
        # Clean up local zips
        if os.path.exists(zip1_path): os.remove(zip1_path)
        if os.path.exists(zip2_path): os.remove(zip2_path)

    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    main()
