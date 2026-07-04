import os
import io
import logging
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

FILE_ID = "1NWiSweAWLLGJMDjp8OVHN2oyXt6Gihd2"
OUTPUT_PATH = r"C:\Users\HP\.gemini\antigravity-ide\brain\c370d570-1fbc-427b-a511-94af4ff83ad7\2022-MERCY_HOUSE_PUBLIC_RETURN.pdf"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(SCRIPT_DIR, "token.json")
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def main():
    if not os.path.exists(TOKEN_FILE):
        logging.error("Missing token_drive_upload.json. Cannot authenticate.")
        return
        
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    drive = build("drive", "v3", credentials=creds)
    
    logging.info(f"Downloading Mercy House PDF from ID {FILE_ID}...")
    try:
        request = drive.files().get_media(fileId=FILE_ID)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            
        with open(OUTPUT_PATH, 'wb') as f:
            f.write(fh.getvalue())
        logging.info(f"✅ Successfully downloaded to {OUTPUT_PATH}")
    except Exception as e:
        logging.error(f"❌ Download failed: {e}")

if __name__ == "__main__":
    main()
