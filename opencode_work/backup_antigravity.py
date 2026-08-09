import os, sys, time, logging, zipfile
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCRIPT_DIR = r"C:\Users\HP\OneDrive\Documents\opencode_work\OSINT_VAULT_BACKUP"
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token_drive_upload.json")
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
BACKUP_DIR = r"C:\Users\HP\OneDrive\Documents\opencode_work_backup"
SRC = r"C:\Users\HP\.gemini\antigravity-ide"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

ts = datetime.now().strftime("%Y%m%d_%H%M%S")
zip_name = f"antigravity_ide_{ts}.zip"
zip_path = os.path.join(BACKUP_DIR, zip_name)

logging.info(f"Zipping {SRC}...")
count = 0
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(SRC):
        dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', '__pycache__', 'antigravity-browser-profile']]
        for f in files:
            if f.endswith(('.zip', '.7z', '.m4a', '.mp3', '.mp4', '.vmdk', '.exe')):
                continue
            fp = os.path.join(root, f)
            arc = os.path.relpath(fp, SRC)
            try:
                zf.write(fp, arc)
                count += 1
            except:
                pass
sz = os.path.getsize(zip_path) / 1024**2
logging.info(f"Zipped {count} files: {sz:.1f} MB")

# Auth + upload
creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
    with open(TOKEN_FILE, 'w') as f:
        f.write(creds.to_json())
drive = build("drive", "v3", credentials=creds)
folder_id = drive.files().list(q="name='sharedall' and mimeType='application/vnd.google-apps.folder' and trashed=false", spaces='drive', fields="files(id, name)").execute()['files'][0]['id']

logging.info(f"Uploading: {zip_name} ({sz:.1f} MB)")
media = MediaFileUpload(zip_path, resumable=True, chunksize=10*1024*1024)
request = drive.files().create(body={'name': zip_name, 'parents': [folder_id]}, media_body=media)
response = None
while response is None:
    status, response = request.next_chunk()
    if status:
        pct = status.progress() * 100
        logging.info(f"  {pct:.0f}%")
logging.info(f"DONE! {response.get('id')}")
print(f"\nUploaded: {zip_name} ({sz:.0f} MB)")
