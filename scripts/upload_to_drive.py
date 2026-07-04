#!/usr/bin/env python3
"""Upload Colab notebooks to Google Drive"""

import os
import json
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_notebooks():
    """Upload all notebooks to Google Drive"""
    
    # Get credentials from environment
    creds_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
    if not creds_json:
        print("⚠️  GOOGLE_CREDENTIALS_JSON not set. Skipping Drive upload.")
        return
    
    # Parse credentials
    creds_dict = json.loads(creds_json)
    credentials = Credentials.from_service_account_info(creds_dict)
    
    # Create Drive API client
    drive_service = build('drive', 'v3', credentials=credentials)
    
    # Find or create "Colab Notebooks" folder
    query = "name='Colab Notebooks' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = drive_service.files().list(q=query, spaces='drive', pageSize=1).execute()
    
    if results['files']:
        folder_id = results['files'][0]['id']
    else:
        # Create folder
        folder_metadata = {
            'name': 'Colab Notebooks',
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
        folder_id = folder.get('id')
    
    print(f"📁 Using folder: {folder_id}")
    
    # Upload notebooks
    notebook_dir = Path('.')
    for notebook in notebook_dir.glob('**/*.ipynb'):
        if '.github' not in str(notebook):  # Skip workflow notebooks
            print(f"📤 Uploading {notebook}...")
            
            # Check if file already exists
            query = f"name='{notebook.name}' and parents='{folder_id}' and trashed=false"
            results = drive_service.files().list(q=query, spaces='drive', pageSize=1).execute()
            
            file_metadata = {
                'name': notebook.name,
                'parents': [folder_id]
            }
            
            media = MediaFileUpload(str(notebook), mimetype='application/json', resumable=True)
            
            if results['files']:
                # Update existing file
                file_id = results['files'][0]['id']
                drive_service.files().update(fileId=file_id, media_body=media).execute()
                print(f"✅ Updated: {notebook.name}")
            else:
                # Create new file
                file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                print(f"✅ Created: {notebook.name} ({file.get('id')})")
    
    print("✅ All notebooks uploaded to Google Drive")

if __name__ == '__main__':
    upload_notebooks()
