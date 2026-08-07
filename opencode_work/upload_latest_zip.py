import os, sys, time, logging
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCRIPT_DIR = r"C:\Users\HP\OneDrive\Documents\opencode_work\OSINT_VAULT_BACKUP"
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token_drive_upload.json")
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
BACKUP_DIR = r"C:\Users\HP\OneDrive\Documents\opencode_work_backup"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
    with open(TOKEN_FILE, 'w') as f:
        f.write(creds.to_json())
drive = build("drive", "v3", credentials=creds)
folder_id = drive.files().list(q="name='sharedall' and mimeType='application/vnd.google-apps.folder' and trashed=false", spaces='drive', fields="files(id, name)").execute()['files'][0]['id']

# Upload the newest opencode_work zip
zips = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith('opencode_work_2026')], reverse=True)
for zip_name in zips[:1]:
    zip_file = os.path.join(BACKUP_DIR, zip_name)
    sz = os.path.getsize(zip_file) / 1024**2
    logging.info(f"Uploading: {zip_name} ({sz:.1f} MB)")
    media = MediaFileUpload(zip_file, resumable=True, chunksize=10*1024*1024)
    request = drive.files().create(body={'name': zip_name, 'parents': [folder_id]}, media_body=media)
    response = start = None
    t0 = time.time()
    while response is None:
        status, response = request.next_chunk()
        if status:
            pct = status.progress() * 100
            mb_up = sz * status.progress()
            logging.info(f"  {pct:.0f}% ({mb_up:.0f}/{sz:.0f} MB)")
    logging.info(f"DONE! {response.get('id')}")
    print(f"Uploaded: {zip_name} ({sz:.0f} MB)")
