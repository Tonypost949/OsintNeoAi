import os
import requests
import zipfile
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "token.json")

# Load credentials and refresh them explicitly
creds = Credentials.from_authorized_user_file(TOKEN_FILE, ["https://www.googleapis.com/auth/drive.readonly"])
if creds.expired and creds.refresh_token:
    creds.refresh(Request())

file_id = "1PMaumLhejJmJkjv2r6PXhWhRYXmP5-Ss"
file_name = r"G:\osint-agent\APT2024filesfull.zip"
extract_dir = r"G:\osint-agent\APT2024_Extracted"

url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
headers = {"Authorization": f"Bearer {creds.token}"}

# Check existing file size
existing_size = 0
if os.path.exists(file_name):
    existing_size = os.path.getsize(file_name)

if existing_size > 0:
    headers["Range"] = f"bytes={existing_size}-"
    print(f"Resuming download from {existing_size} bytes...")
else:
    print("Starting download from beginning...")

with requests.get(url, headers=headers, stream=True) as r:
    r.raise_for_status()
    total_size = int(r.headers.get('content-length', 0)) + existing_size
    downloaded = existing_size
    mode = 'ab' if existing_size > 0 else 'wb'
    
    with open(file_name, mode) as f:
        for chunk in r.iter_content(chunk_size=1024*1024*5): # 5MB chunks
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > existing_size:
                    percent = int((downloaded / total_size) * 100)
                    print(f"Downloaded {percent}% ({downloaded / (1024*1024):.2f} MB / {total_size / (1024*1024):.2f} MB)")

print("Download complete. Extracting...")
os.makedirs(extract_dir, exist_ok=True)
with zipfile.ZipFile(file_name, 'r') as zip_ref:
    zip_ref.extractall(extract_dir)

print(f"Extraction complete. Files are in: {extract_dir}")
for root, dirs, files in os.walk(extract_dir):
    for f in files:
        print(f" - {f}")
