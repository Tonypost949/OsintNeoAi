import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

tokens = [
    "token.json",
    "token_drive_upload.json",
    "token_gmail.json",
    "token_photos.json",
    "token_send.json"
]

for t_file in tokens:
    if os.path.exists(t_file):
        print(f"\n===== File: {t_file} =====")
        try:
            with open(t_file, "r") as f:
                data = json.load(f)
                # Print token details safely
                print(f"Scopes: {data.get('scopes')}")
                print(f"Expiry: {data.get('expiry')}")
                
                # Check actual user info using oauth2 service
                creds = Credentials.from_authorized_user_file(t_file)
                # We can call the userinfo API to see the email
                oauth2_service = build("oauth2", "v2", credentials=creds)
                userinfo = oauth2_service.userinfo().get().execute()
                print(f"Authenticated Account: {userinfo.get('email')}")
        except Exception as e:
            print(f"Error inspecting {t_file}: {e}")
