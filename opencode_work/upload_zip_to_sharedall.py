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

results = drive.files().list(
    q="name='sharedall' and mimeType='application/vnd.google-apps.folder' and trashed=false",
    spaces='drive', fields="files(id, name)").execute()
folder_id = results['files'][0]['id']

# Find the zip that was already created
zips = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith('opencode_work_') and f.endswith('.zip')], reverse=True)
if not zips:
    print("No zip found!")
    sys.exit(1)

zip_file = os.path.join(BACKUP_DIR, zips[0])
sz = os.path.getsize(zip_file) / 1024**2
logging.info(f"Uploading: {zips[0]} ({sz:.1f} MB)")

media = MediaFileUpload(zip_file, resumable=True, chunksize=10*1024*1024)
request = drive.files().create(
    body={'name': zips[0], 'parents': [folder_id]},
    media_body=media
)

response = None
start = time.time()
while response is None:
    status, response = request.next_chunk()
    if status:
        pct = status.progress() * 100
        elapsed = time.time() - start
        mb_up = (sz * status.progress())
        speed = mb_up / elapsed if elapsed > 0 else 0
        logging.info(f"Upload: {pct:.1f}% ({mb_up:.1f}/{sz:.1f} MB) @ {speed:.2f} MB/s")

file_id = response.get('id')
logging.info(f"DONE! File ID: {file_id}")
print(f"\nUploaded to sharedall: {zips[0]}")
