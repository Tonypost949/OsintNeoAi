from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseDownload
import os

token_path = r'C:\Users\HP\OneDrive\Documents\opencode_work\OSINT_VAULT_BACKUP\token_drive_upload.json'
creds = Credentials.from_authorized_user_file(token_path, scopes=['https://www.googleapis.com/auth/drive.readonly'])
drive = build('drive', 'v3', credentials=creds)

SHAREDALL_ID = '1q5bmZJQ9IuSudsie1KNuMWZ0mbfu6-gE'
out_dir = r'C:\Users\HP\OneDrive\Documents\opencode_work\bq_exports'
os.makedirs(out_dir, exist_ok=True)

# Get sharedall folder contents
results = drive.files().list(
    q=f"'{SHAREDALL_ID}' in parents",
    fields='files(id,name,mimeType,size)',
    pageSize=1000
).execute()
files = results.get('files', [])
print(f'Found {len(files)} files in sharedall')

# Also check GCS exports bucket
for f in files:
    if f['name'].endswith('.json'):
        size_mb = int(f.get('size', 0)) / 1024 / 1024
        print(f'Downloading: {f["name"]} ({size_mb:.1f}MB)')
        request = drive.files().get_media(fileId=f['id'])
        path = os.path.join(out_dir, f['name'])
        with open(path, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
        print(f'  Saved to {path}')

print('Done downloading Drive exports')
