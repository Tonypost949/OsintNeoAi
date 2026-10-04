from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os
import io
import zipfile
from googleapiclient.http import MediaIoBaseDownload

TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "token.json")
creds = Credentials.from_authorized_user_file(TOKEN_FILE, ["https://www.googleapis.com/auth/drive.readonly"])
service = build("drive", "v3", credentials=creds)

file_id = "1PMaumLhejJmJkjv2r6PXhWhRYXmP5-Ss"
file_name = r"G:\osint-agent\APT2024filesfull.zip"
extract_dir = r"G:\osint-agent\APT2024_Extracted"

print(f"Downloading to {file_name}...")
request = service.files().get_media(fileId=file_id)

with io.FileIO(file_name, 'wb') as fh:
    downloader = MediaIoBaseDownload(fh, request, chunksize=1024*1024*5) # 5MB chunks
    done = False
    while not done:
        status, done = downloader.next_chunk()
        if status:
            print(f"Downloaded {int(status.progress() * 100)}% ({status.resumable_progress / (1024*1024):.2f} MB)")

print("Download complete. Extracting...")
os.makedirs(extract_dir, exist_ok=True)
with zipfile.ZipFile(file_name, 'r') as zip_ref:
    zip_ref.extractall(extract_dir)

print(f"Extraction complete. Files are in: {extract_dir}")
for root, dirs, files in os.walk(extract_dir):
    for f in files:
        print(f" - {f}")
