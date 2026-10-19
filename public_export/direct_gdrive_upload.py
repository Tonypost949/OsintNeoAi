import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Target source folder
src_dir = r"C:\Amd949609_Antigravity_v1\tasks\anaheim_evidence_audit"
adc_file = r"C:\OsintNeoAi\gcp_adc.json"

print(f"[+] Checking service account ADC file: {adc_file}")

if os.path.exists(adc_file):
    try:
        creds = service_account.Credentials.from_service_account_file(
            adc_file,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        service = build('drive', 'v3', credentials=creds)
        print("[+] Google Drive API Service Initialized!")
        
        # Upload each file directly via API
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
                print(f"[+] DIRECT UPLOADED TO GDRIVE VIA API: {f} -> ID: {uploaded_file.get('id')} | Link: {uploaded_file.get('webViewLink')}")
    except Exception as e:
        print(f"[-] Drive API Direct Upload Note: {e}")
