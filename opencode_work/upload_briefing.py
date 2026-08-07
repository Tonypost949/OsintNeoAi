from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from pathlib import Path
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload

TOKEN_FILE = Path("C:/Users/HP/OneDrive/Documents/opencode_work/OSINT_VAULT_BACKUP/token_drive_upload.json")
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
DRIVE_FOLDER_ID = "1q5bmZJQ9IuSudsie1KNuMWZ0mbfu6-gE"

creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
if not creds.valid:
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, 'w') as t:
            t.write(creds.to_json())
drive = build("drive", "v3", credentials=creds)

local_path = Path("C:/Users/HP/OneDrive/Documents/opencode_work/RICO_ENTERPRISE_BRIEF_v3.md")
file_metadata = {"name": local_path.name, "parents": [DRIVE_FOLDER_ID]}
media = MediaFileUpload(str(local_path), resumable=True)
request = drive.files().create(body=file_metadata, media_body=media, fields="id")
response = None
while response is None:
    status, response = request.next_chunk()
    if status:
        print(f"  Upload: {int(status.progress()*100)}%")
print(f"Uploaded -> {response.get('id')}")
