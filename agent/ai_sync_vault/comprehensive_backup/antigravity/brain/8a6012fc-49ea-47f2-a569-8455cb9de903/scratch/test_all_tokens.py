import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

folder = r"C:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent"
tokens = ["token.json", "token_drive_upload.json", "token_gmail.json", "token_photos.json", "token_send.json"]

for t in tokens:
    path = os.path.join(folder, t)
    if os.path.exists(path):
        try:
            creds = Credentials.from_authorized_user_file(path)
            # Try refreshing
            from google.auth.transport.requests import Request
            creds.refresh(Request())
            print(f"[VALID] {t} is valid and refreshed!")
        except Exception as e:
            print(f"[INVALID] {t} failed: {e}")
