from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from pathlib import Path

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

results = drive.files().list(
    q=f"'{DRIVE_FOLDER_ID}' in parents and trashed=false",
    spaces='drive',
    fields="files(id, name, size)"
).execute()

files = results.get('files', [])
print(f"Total files in sharedall: {len(files)}")

targets = ["ppp_rico_ppp_150k_plus.csv", "ppp_rico_ppp_up_to_150k.csv"]
for target in targets:
    matching = [f for f in files if f['name'] == target]
    chunks = [f for f in files if f['name'].startswith(target + ".part")]
    print(f"\n{target}:")
    print(f"  Full file: {len(matching)} found")
    for m in matching:
        print(f"    {m['name']} - {int(m.get('size',0))/1024/1024:.1f} MB")
    print(f"  Chunks: {len(chunks)} found")
    for c in sorted(chunks, key=lambda x: x['name']):
        print(f"    {c['name']} - {int(c.get('size',0))/1024/1024:.1f} MB")

duplicates = {}
for f in files:
    n = f['name']
    if n not in duplicates:
        duplicates[n] = []
    duplicates[n].append(f['id'])

dupes = {n: ids for n, ids in duplicates.items() if len(ids) > 1 and '.part' in n}
print(f"\nDuplicate chunks to delete: {sum(len(v)-1 for v in dupes.values())} files")
for name, ids in dupes.items():
    print(f"  {name}: keeping {ids[0]}, deleting {len(ids)-1} duplicates")
    for fid in ids[1:]:
        drive.files().delete(fileId=fid).execute()
print("\nCleanup done.")
