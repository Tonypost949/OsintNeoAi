from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os

TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "token.json")
creds = Credentials.from_authorized_user_file(TOKEN_FILE, ["https://www.googleapis.com/auth/drive.readonly"])
service = build("drive", "v3", credentials=creds)

folder_id = "173mY5p0bvl_2SjiGdmExkoOKDYgj_loN"

results = service.files().list(
    q=f"'{folder_id}' in parents and trashed=false",
    fields="files(id, name, mimeType)"
).execute()

files = results.get('files', [])
print(f"Found {len(files)} files in APT2024 folder:")
for f in files:
    print(f"- {f['name']} (ID: {f['id']}) - Mime: {f['mimeType']}")
