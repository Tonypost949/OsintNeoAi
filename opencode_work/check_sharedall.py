"""Check Drive sharedall folder contents"""
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")
TOKEN_FILE = WORK_DIR / "OSINT_VAULT_BACKUP" / "token_drive_upload.json"
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
FOLDER_ID = "1q5bmZJQ9IuSudsie1KNuMWZ0mbfu6-gE"

creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
if not creds.valid:
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, "w") as t:
            t.write(creds.to_json())

drive = build("drive", "v3", credentials=creds)

results = []
page_token = None
while True:
    files = drive.files().list(
        q=f"'{FOLDER_ID}' in parents",
        fields="files(id,name,size),nextPageToken",
        pageSize=200,
        pageToken=page_token
    ).execute()
    for f in files.get("files", []):
        results.append(f)
    page_token = files.get("nextPageToken")
    if not page_token:
        break

print(f"Total files in sharedall: {len(results)}")
for f in sorted(results, key=lambda x: x["name"]):
    sz = int(f.get("size", 0))
    print(f"  {f['name']} ({sz//1024}KB)")
