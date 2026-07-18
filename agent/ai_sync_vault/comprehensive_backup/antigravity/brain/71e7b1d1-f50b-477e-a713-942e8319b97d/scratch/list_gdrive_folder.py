import os
import sys
import google.auth
from google.auth.transport.requests import Request
import requests

folder_id = "173mY5p0bvl_2SjiGdmExkoOKDYgj_loN"

print("Attempting to load Google credentials...")
try:
    credentials, project = google.auth.default(
        scopes=['https://www.googleapis.com/auth/drive.readonly']
    )
    print(f"Loaded credentials. Project: {project}")
    
    # Refresh credentials to get access token
    credentials.refresh(Request())
    print("Successfully refreshed credentials.")
    
    # Query Google Drive API for files in folder
    url = "https://www.googleapis.com/drive/v3/files"
    headers = {
        "Authorization": f"Bearer {credentials.token}"
    }
    
    params = {
        "q": f"'{folder_id}' in parents and trashed = false",
        "pageSize": 50,
        "fields": "nextPageToken, files(id, name, mimeType, webViewLink, size, modifiedTime)",
        "supportsAllDrives": "true",
        "includeItemsFromAllDrives": "true"
    }
    
    print(f"Querying Google Drive folder: {folder_id}...")
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        files = data.get("files", [])
        print(f"\nSUCCESS! Found {len(files)} files in folder:")
        for f in files:
            print(f"- Name: {f['name']}")
            print(f"  ID: {f['id']}")
            print(f"  MimeType: {f['mimeType']}")
            print(f"  Link: {f.get('webViewLink', 'N/A')}")
            print(f"  Size: {f.get('size', 'N/A')} bytes")
            print(f"  Modified: {f.get('modifiedTime', 'N/A')}\n")
    else:
        print(f"Drive API Error {response.status_code}: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")
