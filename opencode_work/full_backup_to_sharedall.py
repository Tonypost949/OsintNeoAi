import os, sys, zipfile, logging
from pathlib import Path
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCRIPT_DIR = r"C:\Users\HP\OneDrive\Documents\opencode_work\OSINT_VAULT_BACKUP"
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token_drive_upload.json")
CLIENT_SECRETS_FILE = os.path.join(SCRIPT_DIR, "client_secret.json")
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
TARGET_FOLDER = "sharedall"

BACKUP_DIR = r"C:\Users\HP\OneDrive\Documents\opencode_work_backup"
os.makedirs(BACKUP_DIR, exist_ok=True)
ts = datetime.now().strftime("%Y%m%d_%H%M%S")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

# Auth
creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
    with open(TOKEN_FILE, 'w') as f:
        f.write(creds.to_json())
drive = build("drive", "v3", credentials=creds)

# Find sharedall folder
results = drive.files().list(
    q="name='sharedall' and mimeType='application/vnd.google-apps.folder' and trashed=false",
    spaces='drive', fields="files(id, name)").execute()
items = results.get('files', [])
if items:
    folder_id = items[0]['id']
    logging.info(f"Found sharedall: {folder_id}")
else:
    logging.info("Creating sharedall...")
    folder_id = drive.files().create(
        body={'name': 'sharedall', 'mimeType': 'application/vnd.google-apps.folder'},
        fields='id').execute()['id']

# === BACKUP 1: opencode_work ===
src1 = r"C:\Users\HP\OneDrive\Documents\opencode_work"
zip1 = os.path.join(BACKUP_DIR, f"opencode_work_{ts}.zip")
logging.info(f"Zipping {src1}...")
with zipfile.ZipFile(zip1, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(src1):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.vscode', 'venv']]
        for f in files:
            fp = os.path.join(root, f)
            arcname = os.path.relpath(fp, src1)
            try:
                zf.write(fp, arcname)
            except:
                pass
sz1 = os.path.getsize(zip1) / 1024**2
logging.info(f"Zipped: {sz1:.1f} MB")

logging.info("Uploading opencode_work...")
media = MediaFileUpload(zip1, resumable=True)
drive.files().create(body={'name': os.path.basename(zip1), 'parents': [folder_id]}, media_body=media).execute()
logging.info("Uploaded opencode_work!")

# === BACKUP 2: antigravity IDE brain ===
src2 = r"C:\Users\HP\.gemini\antigravity-ide"
if os.path.exists(src2):
    zip2 = os.path.join(BACKUP_DIR, f"antigravity_ide_{ts}.zip")
    logging.info(f"Zipping {src2}...")
    with zipfile.ZipFile(zip2, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(src2):
            dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', '__pycache__']]
            for f in files:
                if f.endswith('.zip') or f.endswith('.z7'):
                    continue
                fp = os.path.join(root, f)
                arcname = os.path.relpath(fp, src2)
                try:
                    zf.write(fp, arcname)
                except:
                    pass
    sz2 = os.path.getsize(zip2) / 1024**2
    logging.info(f"Zipped: {sz2:.1f} MB")

    logging.info("Uploading antigravity IDE...")
    media2 = MediaFileUpload(zip2, resumable=True)
    drive.files().create(body={'name': os.path.basename(zip2), 'parents': [folder_id]}, media_body=media2).execute()
    logging.info("Uploaded antigravity IDE!")

logging.info("=== ALL DONE ===")
print(f"\nBackups in sharedall:")
print(f"  {os.path.basename(zip1)} ({sz1:.0f} MB)")
print(f"  {os.path.basename(zip2)} ({sz2:.0f} MB)")
