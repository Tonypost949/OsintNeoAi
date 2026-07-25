import os
import logging
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")
SCRIPT_DIR = WORK_DIR / "OSINT_VAULT_BACKUP"
TOKEN_FILE = SCRIPT_DIR / "token_drive_upload.json"
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
DRIVE_FOLDER_ID = "1q5bmZJQ9IuSudsie1KNuMWZ0mbfu6-gE"

creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
if not creds.valid:
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, 'w') as t:
            t.write(creds.to_json())
drive = build("drive", "v3", credentials=creds)

CHUNK_SIZE = 100 * 1024 * 1024

def upload_file(path, name, folder_id):
    file_metadata = {"name": name, "parents": [folder_id]}
    media = MediaFileUpload(str(path), chunksize=CHUNK_SIZE, resumable=True)
    request = drive.files().create(body=file_metadata, media_body=media, fields="id")
    response = None
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                logging.info(f"  {name}: {int(status.progress()*100)}%")
        except Exception as e:
            logging.warning(f"  Retry {name}: {e}")
            import time; time.sleep(3)
            continue
    return response.get("id")

def split_and_upload(local_path, base_name, folder_id):
    chunks = []
    i = 0
    with open(local_path, 'rb') as f:
        while True:
            data = f.read(CHUNK_SIZE)
            if not data:
                break
            chunk_name = f"{base_name}.part{i:03d}"
            chunk_path = WORK_DIR / f"chunk_{i:03d}.dat"
            with open(chunk_path, 'wb') as c:
                c.write(data)
            chunks.append((chunk_name, chunk_path))
            i += 1

    logging.info(f"Split into {len(chunks)} chunks, uploading...")
    for chunk_name, chunk_path in chunks:
        fid = upload_file(chunk_path, chunk_name, folder_id)
        logging.info(f"  -> {chunk_name} -> {fid}")
        try:
            os.remove(chunk_path)
        except Exception:
            pass

large_files = [
    ("ppp_rico_ppp_150k_plus.csv", WORK_DIR / "ppp_rico_ppp_150k_plus.csv"),
    ("ppp_rico_ppp_up_to_150k.csv", WORK_DIR / "ppp_rico_ppp_up_to_150k.csv"),
]

for base_name, local_path in large_files:
    if not local_path.exists():
        logging.info(f"NOT FOUND: {base_name}")
        continue
    size_mb = local_path.stat().st_size / 1024 / 1024
    logging.info(f"UPLOAD {base_name} ({size_mb:.1f} MB)...")
    split_and_upload(local_path, base_name, DRIVE_FOLDER_ID)

logging.info("All done.")
