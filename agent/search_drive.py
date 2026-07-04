from google.cloud import bigquery
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os
import io
from googleapiclient.http import MediaIoBaseDownload

bq_client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

query = """
SELECT file_id, file_name, mime_type, web_view_link
FROM `project-743aab84-f9a5-4ec7-954.national_audits.drive_file_index`
WHERE LOWER(file_name) LIKE '%apt%2024%'
   OR LOWER(file_name) LIKE '%isoont%'
   OR LOWER(file_name) LIKE '%osint%'
"""

try:
    results = bq_client.query(query).result()
    files = list(results)
    print(f"Found {len(files)} files matching criteria.")
    
    # Authenticate to Drive to download them
    TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "token.json")
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, ["https://www.googleapis.com/auth/drive.readonly"])
        service = build("drive", "v3", credentials=creds)
        
        for f in files:
            print(f"File: {f.file_name} (ID: {f.file_id})")
            file_id = f.file_id
            mime_type = f.mime_type
            
            try:
                if 'application/vnd.google-apps' in mime_type:
                    # Export Google Workspace docs as text
                    export_mime = 'text/plain'
                    if 'spreadsheet' in mime_type:
                        export_mime = 'text/csv'
                    
                    request = service.files().export_media(fileId=file_id, mimeType=export_mime)
                else:
                    request = service.files().get_media(fileId=file_id)
                    
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                
                content = fh.getvalue().decode('utf-8', errors='ignore')
                print(f"--- CONTENT OF {f.file_name} ---")
                print(content[:2000]) # Print first 2000 chars
                print("-" * 40)
            except Exception as e:
                print(f"Error downloading {f.file_name}: {e}")
    else:
        print("No token.json found to download files.")
        for f in files:
            print(f"File: {f.file_name} - Link: {f.web_view_link}")

except Exception as e:
    print(f"Error querying BigQuery: {e}")
