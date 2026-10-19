import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

src_dir = r"C:\Amd949609_Antigravity_v1\tasks\anaheim_evidence_audit"
adc_file = r"C:\OsintNeoAi\gcp_adc.json"

print(f"[+] Initializing OAuth User Credentials from {adc_file}...")

try:
    with open(adc_file, "r") as f:
        info = json.load(f)
        
    # Standard GCP user credentials without scope restriction
    creds = Credentials(
        token=None,
        refresh_token=info["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=info["client_id"],
        client_secret=info["client_secret"]
    )
    
    service = build('drive', 'v3', credentials=creds)
    print("[+] Google Drive API Authenticated & Active for User Account!")
    
    for f in os.listdir(src_dir):
        file_path = os.path.join(src_dir, f)
        if os.path.isfile(file_path):
            file_metadata = {'name': f'Anaheim_Evidence_Backup_{f}'}
            media = MediaFileUpload(file_path, resumable=True)
            uploaded_file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()
            print(f"[+] DIRECT LIVE UPLOAD: {f} -> ID: {uploaded_file.get('id')} | Link: {uploaded_file.get('webViewLink')}")
            
except Exception as e:
    print(f"[-] OAuth Drive Upload Error: {e}")
