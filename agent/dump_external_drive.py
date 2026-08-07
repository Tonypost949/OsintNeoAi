import os
import sys
import logging
import time
import socket
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
from httplib2 import ServerNotFoundError

# Force standard streams to handle emojis and special characters on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='backslashreplace')

# ----------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------
SOURCE_DIR = r"G:\\"
DRIVE_ROOT_FOLDER_NAME = "sharedall"
BACKUP_SUBFOLDER_NAME = "G_Drive_Backup_20260622"

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRETS_FILE = os.path.join(SCRIPT_DIR, "client_secret.json")
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token_drive_upload.json")

# Set up logging
log_file = os.path.join(SCRIPT_DIR, "dump_external_drive.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

def get_drive_service():
    """Authenticate and return a Drive service object."""
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

def call_with_retry(func, *args, **kwargs):
    """Executes a function, retrying indefinitely on network connection failures."""
    while True:
        try:
            return func(*args, **kwargs)
        except (ServerNotFoundError, socket.gaierror, ConnectionError, TimeoutError) as e:
            logging.warning(f"Network error occurred: {e}. Internet connection might be down. Retrying in 10 seconds...")
            time.sleep(10)
        except Exception as e:
            # Check if exception is HttpError with standard socket error inside
            if "Unable to find the server" in str(e) or "getaddrinfo failed" in str(e):
                logging.warning(f"Connection issue detected: {e}. Retrying in 10 seconds...")
                time.sleep(10)
            else:
                raise

def ensure_folder_exists(service, folder_name, parent_id=None):
    """Check if folder exists under parent_id, otherwise create it."""
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    
    def run():
        results = service.files().list(
            q=query,
            spaces='drive',
            fields="files(id, name)"
        ).execute()
        
        items = results.get('files', [])
        if not items:
            logging.info(f"Creating folder '{folder_name}' (parent: {parent_id})...")
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            if parent_id:
                file_metadata['parents'] = [parent_id]
            folder = service.files().create(body=file_metadata, fields='id').execute()
            return folder.get('id')
        return items[0].get('id')

    return call_with_retry(run)

def upload_file_resumable(service, local_path, parent_id):
    """Uploads a file using MediaFileUpload resumable interface with retries."""
    file_metadata = {
        "name": local_path.name,
        "parents": [parent_id]
    }
    
    # Check if file already exists in this folder to avoid duplicates
    def check_exists():
        query = f"name='{local_path.name}' and '{parent_id}' in parents and trashed=false"
        results = service.files().list(q=query, fields="files(id)").execute()
        if results.get('files'):
            return results.get('files')[0]['id']
        return None

    existing_id = call_with_retry(check_exists)
    if existing_id:
        logging.info(f"File {local_path.name} already exists in target folder. Skipping.")
        return existing_id

    media = MediaFileUpload(str(local_path), chunksize=1024*1024, resumable=True)
    request = service.files().create(body=file_metadata, media_body=media, fields="id")
    
    response = None
    retries = 3
    while response is None:
        try:
            # Wrap the upload chunk call in the network retry logic
            def next_chunk_call():
                return request.next_chunk()
            
            status, response = call_with_retry(next_chunk_call)
            if status:
                logging.info(f"Uploading {local_path.name}: {int(status.progress() * 100)}% complete")
        except HttpError as e:
            if e.resp.status in [500, 502, 503, 504]:
                retries -= 1
                if retries < 0:
                    raise
                logging.warning(f"Transient HTTP error {e.resp.status}. Retrying chunk in 5 seconds...")
                time.sleep(5)
            else:
                raise
    return response.get("id")

def main():
    logging.info("Starting external drive backup script...")
    if not os.path.exists(SOURCE_DIR):
        logging.error(f"Source directory {SOURCE_DIR} does not exist!")
        return

    service = call_with_retry(get_drive_service)
    
    # 1. Ensure root 'sharedall' folder exists
    sharedall_id = ensure_folder_exists(service, DRIVE_ROOT_FOLDER_NAME)
    logging.info(f"Root folder '{DRIVE_ROOT_FOLDER_NAME}' ID: {sharedall_id}")

    # 2. Ensure specific backup subfolder exists
    backup_root_id = ensure_folder_exists(service, BACKUP_SUBFOLDER_NAME, parent_id=sharedall_id)
    logging.info(f"Backup subfolder '{BACKUP_SUBFOLDER_NAME}' ID: {backup_root_id}")

    # Cache folder IDs to speed up processing
    # Key: relative path from G:\ (e.g. "archives/2026"), Value: Drive folder ID
    folder_cache = {"": backup_root_id}

    for dirpath, dirnames, filenames in os.walk(SOURCE_DIR):
        # Skip system or hidden dirs if needed
        # e.g., System Volume Information, $RECYCLE.BIN
        dirpath_path = Path(dirpath)
        parts = dirpath_path.parts
        if any(p.startswith('$') or p == 'System Volume Information' or p == '.gemini' for p in parts):
            continue

        # Get path relative to G:\
        try:
            rel_path = dirpath_path.relative_to(SOURCE_DIR)
            rel_str = str(rel_path).replace("\\", "/")
            if rel_str == ".":
                rel_str = ""
        except ValueError:
            continue

        # Get parent folder's Drive ID
        if rel_str not in folder_cache:
            # We need to build the folder path sequentially in Google Drive
            parent_rel = str(rel_path.parent).replace("\\", "/")
            if parent_rel == ".":
                parent_rel = ""
            
            parent_drive_id = folder_cache.get(parent_rel)
            if not parent_drive_id:
                # If parent isn't in cache, something is out of order, but walk should guarantee it.
                logging.error(f"Parent path {parent_rel} not found in cache.")
                continue
            
            folder_id = ensure_folder_exists(service, dirpath_path.name, parent_id=parent_drive_id)
            folder_cache[rel_str] = folder_id
        
        current_folder_id = folder_cache[rel_str]

        # Upload files in this directory
        for filename in filenames:
            file_path = dirpath_path / filename
            # Skip system/hidden files
            if filename.startswith("~$") or filename.startswith("."):
                continue
            
            try:
                logging.info(f"Processing: {file_path}")
                upload_file_resumable(service, file_path, current_folder_id)
            except Exception as e:
                logging.error(f"Failed to upload {file_path}: {e}")

    logging.info("Backup job finished successfully!")

if __name__ == "__main__":
    main()
