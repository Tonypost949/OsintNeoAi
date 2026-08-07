from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from pathlib import Path

SCRIPT_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work/OSINT_VAULT_BACKUP")
TOKEN_FILE = SCRIPT_DIR / "token_drive_upload.json"
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
drive = build("drive", "v3", credentials=creds)

results = drive.files().list(
    q="name contains 'sharedall' and mimeType='application/vnd.google-apps.folder' and trashed=false",
    spaces='drive',
    fields="files(id, name)"
).execute()
items = results.get('files', [])
print(f"Found {len(items)} folders:")
for item in items:
    print(f"  {item['name']} -> {item['id']}")
