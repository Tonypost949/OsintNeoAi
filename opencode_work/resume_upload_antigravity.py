import os, sys, logging
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCRIPT_DIR = r"C:\Users\HP\OneDrive\Documents\opencode_work\OSINT_VAULT_BACKUP"
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token_drive_upload.json")
BACKUP_DIR = r"C:\Users\HP\OneDrive\Documents\opencode_work_backup"

logging.basicConfig(level=logging.INFO, format="%(asctime)s UPLOAD %(message)s")

creds = Credentials.from_authorized_user_file(TOKEN_FILE, ["https://www.googleapis.com/auth/drive.file"])
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
    with open(TOKEN_FILE, 'w') as f:
        f.write(creds.to_json())
drive = build("drive", "v3", credentials=creds)
folder_id = drive.files().list(q="name='sharedall' and mimeType='application/vnd.google-apps.folder' and trashed=false", spaces='drive', fields="files(id, name)").execute()['files'][0]['id']

# Find the newest antigravity zip
zips = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith('antigravity_projects_')], reverse=True)
if not zips:
    print("No antigravity zip found!")
    sys.exit(1)

zip_file = os.path.join(BACKUP_DIR, zips[0])
sz = os.path.getsize(zip_file) / 1024**2
logging.info(f"Resuming upload: {zips[0]} ({sz:.0f} MB)")

# Check if file already exists in Drive (partial upload)
existing = drive.files().list(
    q=f"name='{zips[0]}' and '{folder_id}' in parents and trashed=false",
    spaces='drive', fields="files(id, name, size)").execute().get('files', [])
if existing:
    logging.info(f"Already exists, removing: {existing[0]['id']}")
    drive.files().delete(fileId=existing[0]['id']).execute()

media = MediaFileUpload(zip_file, resumable=True, chunksize=10*1024*1024)
request = drive.files().create(body={'name': zips[0], 'parents': [folder_id]}, media_body=media)
response = None
while response is None:
    status, response = request.next_chunk()
    if status:
        logging.info(f"{status.progress()*100:.0f}% ({sz*status.progress():.0f}/{sz:.0f} MB)")

logging.info(f"DONE! ID: {response.get('id')}")
print(f"\nUploaded: {zips[0]} ({sz:.0f} MB) to sharedall")
