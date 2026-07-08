from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from pathlib import Path

TOKEN_FILE = Path("C:/Users/HP/OneDrive/Documents/opencode_work/OSINT_VAULT_BACKUP/token_drive_upload.json")
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
DRIVE_FOLDER_ID = "1q5bmZJQ9IuSudsie1KNuMWZ0mbfu6-gE"

creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
drive = build("drive", "v3", credentials=creds)

results = drive.files().list(
    q=f"'{DRIVE_FOLDER_ID}' in parents and trashed=false",
    spaces='drive',
    fields="files(id, name, size)"
).execute()

files = results.get('files', [])
print(f"Files in sharedall: {len(files)}")
total_mb = 0
for f in sorted(files, key=lambda x: x.get('size', 0), reverse=True):
    sz = int(f.get('size', 0))
    total_mb += sz / 1024 / 1024
    print(f"  {f['name']} - {sz/1024/1024:.1f} MB")

print(f"\nTotal: {total_mb:.1f} MB")
