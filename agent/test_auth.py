import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SD = r'c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent'

print("--- Testing Gmail ---")
try:
    creds = Credentials.from_authorized_user_file(os.path.join(SD, 'token_gmail.json'), ['https://www.googleapis.com/auth/gmail.readonly'])
    if not creds.valid: creds.refresh(Request())
    g = build('gmail', 'v1', credentials=creds)
    profile = g.users().getProfile(userId='me').execute()
    print(f"Gmail OK: {profile['emailAddress']} ({profile['messagesTotal']} messages)")
except Exception as e:
    print(f"Gmail FAIL: {e}")

print("--- Testing Drive ---")
try:
    creds = Credentials.from_authorized_user_file(os.path.join(SD, 'token.json'), ['https://www.googleapis.com/auth/drive.readonly'])
    if not creds.valid: creds.refresh(Request())
    d = build('drive', 'v3', credentials=creds)
    about = d.about().get(fields='user').execute()
    print(f"Drive OK: {about['user']['emailAddress']}")
except Exception as e:
    print(f"Drive FAIL: {e}")

print("--- Testing Photos ---")
try:
    creds = Credentials.from_authorized_user_file(os.path.join(SD, 'token_photos.json'), ['https://www.googleapis.com/auth/photoslibrary.readonly'])
    if not creds.valid: creds.refresh(Request())
    p = build('photoslibrary', 'v1', credentials=creds, static_discovery=False)
    r = p.mediaItems().list(pageSize=1).execute()
    print(f"Photos OK: {len(r.get('mediaItems',[]))} items returned")
except Exception as e:
    print(f"Photos FAIL: {e}")
