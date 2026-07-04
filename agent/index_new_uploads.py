# ============================================================================
# index_new_uploads.py — Index sharedall Drive uploads into BigQuery
# Purpose: Instantly catalog new files without full Drive scan
# ============================================================================

import os, sys, json, logging
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.cloud import bigquery

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = r"C:\Users\HP\OneDrive\Documents\opencode_work\OSINT_VAULT_BACKUP\token_drive_upload.json"
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
TARGET_FOLDER = "sharedall"
PROJECT = "project-743aab84-f9a5-4ec7-954"
DATASET = "national_audits"
TABLE = "drive_file_index"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

def get_drive():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
    return build("drive", "v3", credentials=creds)

def get_bq():
    return bigquery.Client(project=PROJECT)

def main():
    drive = get_drive()
    bq = get_bq()
    
    # Find sharedall folder
    results = drive.files().list(
        q=f"name='{TARGET_FOLDER}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
        spaces='drive', fields="files(id, name)").execute()
    folder_id = results['files'][0]['id']
    
    # List new files (last 7 days)
    files = drive.files().list(
        q=f"'{folder_id}' in parents and trashed=false",
        orderBy="createdTime desc",
        pageSize=50,
        fields="files(id, name, mimeType, size, createdTime, modifiedTime, webViewLink)").execute()
    
    uploaded = []
    for f in files.get('files', []):
        row = {
            'file_id': f['id'],
            'file_name': f['name'],
            'mime_type': f.get('mimeType', ''),
            'size_bytes': f.get('size', '0'),
            'created_time': f.get('createdTime', ''),
            'modified_time': f.get('modifiedTime', ''),
            'web_view_link': f.get('webViewLink', ''),
            'parent_folder_ids': [folder_id],
            'scan_timestamp': datetime.now().isoformat()
        }
        uploaded.append(row)
        logging.info(f"  {f['name']} ({int(f.get('size', 0))/1024**2:.0f} MB)")
    
    logging.info(f"Found {len(uploaded)} files")
    
    # Write to BigQuery
    if uploaded:
        table_ref = f"{PROJECT}.{DATASET}.{TABLE}"
        errors = bq.insert_rows_json(table_ref, uploaded)
        if errors:
            logging.error(f"BigQuery errors: {errors}")
        else:
            logging.info(f"Inserted {len(uploaded)} rows into {table_ref}")
    
    # Save local index
    out = os.path.join(SCRIPT_DIR, "drive_upload_index.json")
    with open(out, 'w') as f:
        json.dump(uploaded, f, indent=2, default=str)
    logging.info(f"Local index: {out}")
    
    return uploaded

if __name__ == "__main__":
    main()
