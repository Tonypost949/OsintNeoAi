import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

tokens = {
    "token.json": ["https://www.googleapis.com/auth/drive.readonly"],
    "token_drive_upload.json": ["https://www.googleapis.com/auth/drive.file"],
    "token_gmail.json": ["https://www.googleapis.com/auth/gmail.readonly"],
    "token_photos.json": ["https://www.googleapis.com/auth/photoslibrary.readonly"],
    "token_send.json": ["https://www.googleapis.com/auth/gmail.send"]
}

for t_file, scopes in tokens.items():
    if os.path.exists(t_file):
        print(f"\n===== Checking Token File: {t_file} =====")
        try:
            creds = Credentials.from_authorized_user_file(t_file, scopes)
            
            # If it's a Gmail token, we can get the profile info and message count
            if "gmail" in scopes[0]:
                service = build("gmail", "v1", credentials=creds)
                profile = service.users().getProfile(userId="me").execute()
                print(f"Gmail Address: {profile.get('emailAddress')}")
                print(f"Total Messages: {profile.get('messagesTotal')}")
                print(f"Total Threads: {profile.get('threadsTotal')}")
            else:
                # For drive or photos, just print that it exists
                print(f"Token is valid for scopes: {scopes}")
        except Exception as e:
            print(f"Error checking {t_file}: {e}")
