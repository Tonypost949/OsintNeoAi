import logging
from pathlib import Path
from google.cloud import storage
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

PROJECT = "noble-beanbag-497411-m4"
BUCKET = "osint-ai-evidence-vault-m4"
DRIVE_FOLDER_ID = "1q5bmZJQ9IuSudsie1KNuMWZ0mbfu6-gE"
WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")
SCRIPT_DIR = WORK_DIR / "OSINT_VAULT_BACKUP"
TOKEN_FILE = SCRIPT_DIR / "token_drive_upload.json"
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

storage_client = storage.Client(project=PROJECT)
bucket = storage_client.bucket(BUCKET)

creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
if not creds.valid:
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, 'w') as t:
            t.write(creds.to_json())
drive = build("drive", "v3", credentials=creds)

large_files = [
    "ppp_rico_ppp_150k_plus.csv",
    "ppp_rico_ppp_up_to_150k.csv",
]

for fname in large_files:
    local_path = WORK_DIR / fname
    if not local_path.exists():
        logging.info(f"NOT FOUND: {fname}")
        continue

    size_mb = local_path.stat().st_size / 1024 / 1024
    gcs_name = f"sharedall_drive/{fname}"

    logging.info(f"1. Upload {fname} ({size_mb:.1f} MB) to GCS...")
    blob = bucket.blob(gcs_name)
    try:
        blob.upload_from_filename(str(local_path), timeout=600)
        logging.info(f"   GCS upload done: gs://{BUCKET}/{gcs_name}")
    except Exception as e:
        logging.error(f"   GCS upload failed: {e}")
        continue

    logging.info(f"2. Create Drive shortcut to GCS file...")
    try:
        file_metadata = {
            "name": fname,
            "parents": [DRIVE_FOLDER_ID],
            "appProperties": {"gcsUri": f"gs://{BUCKET}/{gcs_name}"}
        }
        created = drive.files().create(body=file_metadata, fields="id, name").execute()
        logging.info(f"   Drive file created: {created['id']} ({created['name']})")
    except Exception as e:
        logging.error(f"   Drive shortcut failed: {e}")

logging.info("All done.")
