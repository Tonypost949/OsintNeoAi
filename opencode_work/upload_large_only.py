import logging
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

SCRIPT_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work/OSINT_VAULT_BACKUP")
TOKEN_FILE = SCRIPT_DIR / "token_drive_upload.json"
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")
DRIVE_FOLDER_ID = "1q5bmZJQ9IuSudsie1KNuMWZ0mbfu6-gE"

creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
if not creds.valid:
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, 'w') as t:
            t.write(creds.to_json())
drive = build("drive", "v3", credentials=creds)

def upload_file(local_path, name, folder_id):
    file_metadata = {"name": name, "parents": [folder_id]}
    media = MediaFileUpload(str(local_path), resumable=True, chunksize=1024*1024*50)
    request = drive.files().create(body=file_metadata, media_body=media, fields="id")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            logging.info(f"  {name}: {int(status.progress()*100)}%")
    return response.get("id")

large_files = [
    ("ppp_rico_ppp_150k_plus.csv", WORK_DIR / "ppp_rico_ppp_150k_plus.csv"),
    ("ppp_rico_ppp_up_to_150k.csv", WORK_DIR / "ppp_rico_ppp_up_to_150k.csv"),
]

for name, path in large_files:
    if not path.exists():
        logging.info(f"NOT FOUND: {name}")
        continue
    size_mb = path.stat().st_size / 1024 / 1024
    logging.info(f"UPLOAD {name} ({size_mb:.1f} MB)...")
    try:
        file_id = upload_file(path, name, DRIVE_FOLDER_ID)
        logging.info(f"  -> {file_id}")
    except Exception as e:
        logging.error(f"  ERROR: {e}")

logging.info("Done.")
