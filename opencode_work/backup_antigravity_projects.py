import os, sys, logging, zipfile
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCRIPT_DIR = r"C:\Users\HP\OneDrive\Documents\opencode_work\OSINT_VAULT_BACKUP"
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token_drive_upload.json")
BACKUP_DIR = r"C:\Users\HP\OneDrive\Documents\opencode_work_backup"
IDE = r"C:\Users\HP\.gemini\antigravity-ide"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
ts = datetime.now().strftime("%Y%m%d_%H%M%S")

# Zip brain + scratch + conversations (critical project data only)
zip_name = f"antigravity_projects_{ts}.zip"
zip_path = os.path.join(BACKUP_DIR, zip_name)

folders_to_backup = ['brain', 'scratch', 'conversations']
count = 0
logging.info(f"Zipping: {folders_to_backup}")
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for folder_name in folders_to_backup:
        fpath = os.path.join(IDE, folder_name)
        if not os.path.exists(fpath):
            continue
        for root, dirs, files in os.walk(fpath):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for f in files:
                if f.endswith(('.zip', '.7z', '.m4a', '.mp3', '.mp4', '.vmdk', '.exe', '.db', '.wim')):
                    continue
                fp = os.path.join(root, f)
                arc = os.path.relpath(fp, IDE)
                try:
                    if os.path.getsize(fp) < 100*1024*1024:  # skip >100MB files
                        zf.write(fp, arc)
                        count += 1
                    else:
                        logging.info(f"  SKIP large: {arc} ({os.path.getsize(fp)/1024**2:.0f} MB)")
                except:
                    pass

sz = os.path.getsize(zip_path) / 1024**2
logging.info(f"Zipped {count} files: {sz:.1f} MB")

# Upload
creds = Credentials.from_authorized_user_file(TOKEN_FILE, ["https://www.googleapis.com/auth/drive.file"])
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
    with open(TOKEN_FILE, 'w') as f:
        f.write(creds.to_json())
drive = build("drive", "v3", credentials=creds)
folder_id = drive.files().list(q="name='sharedall' and mimeType='application/vnd.google-apps.folder' and trashed=false", spaces='drive', fields="files(id, name)").execute()['files'][0]['id']

logging.info(f"Uploading {sz:.0f} MB to sharedall...")
media = MediaFileUpload(zip_path, resumable=True, chunksize=10*1024*1024)
request = drive.files().create(body={'name': zip_name, 'parents': [folder_id]}, media_body=media)
response = None
while response is None:
    status, response = request.next_chunk()
    if status: logging.info(f"  {status.progress()*100:.0f}%")
logging.info(f"DONE! {response.get('id')}")
print(f"\nUploaded: {zip_name} ({sz:.0f} MB)")
