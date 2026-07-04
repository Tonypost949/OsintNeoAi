from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os

TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "token.json")
creds = Credentials.from_authorized_user_file(TOKEN_FILE, ["https://www.googleapis.com/auth/drive.readonly"])
service = build("drive", "v3", credentials=creds)

file_id = "1PMaumLhejJmJkjv2r6PXhWhRYXmP5-Ss"
file = service.files().get(fileId=file_id, fields="id, name, size, mimeType").execute()
print(f"File Name: {file.get('name')}")
print(f"Mime Type: {file.get('mimeType')}")
print(f"Size: {file.get('size')} bytes")
