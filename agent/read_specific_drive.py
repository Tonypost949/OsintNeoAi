from google.cloud import bigquery
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os
import io
from googleapiclient.http import MediaIoBaseDownload
import shutil

# --- CHECK STORAGE ---
def check_storage():
    print("--- PC STORAGE HEALTH ---")
    total, used, free = shutil.disk_usage("C:\\")
    free_gb = free / (1024 ** 3)
    total_gb = total / (1024 ** 3)
    percent_free = (free / total) * 100
    
    print(f"C: Drive Space: {free_gb:.1f} GB free out of {total_gb:.1f} GB ({percent_free:.1f}% free)")
    if percent_free < 15.0:
        print("WARNING: Disk space is getting low! Time to move large files to the cloud vault.")
    else:
        print("Disk space is healthy.")
    print("-" * 25)

check_storage()

# --- FETCH SPECIFIC DRIVE FILES ---
file_ids = {
    "APT2024 china spy": "173mY5p0bvl_2SjiGdmExkoOKDYgj_loN",
    "OSINT Skill and Master Sheet Update": "1MquXKO5W7-JXfsJDzcHlk-auV9_9gznxHhNjkedu2ic"
}

TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "token.json")
if os.path.exists(TOKEN_FILE):
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, ["https://www.googleapis.com/auth/drive.readonly"])
    service = build("drive", "v3", credentials=creds)
    
    for name, file_id in file_ids.items():
        print(f"Attempting to download {name}...")
        try:
            # Get metadata to see what kind of file it is
            meta = service.files().get(fileId=file_id).execute()
            mime = meta.get('mimeType')
            print(f"Mime type: {mime}")
            
            if 'application/vnd.google-apps' in mime:
                if 'spreadsheet' in mime:
                    export_mime = 'text/csv'
                elif 'document' in mime:
                    export_mime = 'text/plain'
                else:
                    export_mime = 'application/pdf' # fallback
                request = service.files().export_media(fileId=file_id, mimeType=export_mime)
            else:
                request = service.files().get_media(fileId=file_id)
                
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            # Save it to disk instead of printing to avoid encoding errors
            ext = ".txt"
            if mime == "application/pdf": ext = ".pdf"
            elif mime == "text/csv": ext = ".csv"
            
            out_file = f"{name}{ext}"
            with open(out_file, "wb") as f:
                f.write(fh.getvalue())
            print(f"✅ Successfully saved to {out_file}")
            
            # If text/csv, try to print a preview
            if ext in [".txt", ".csv"]:
                try:
                    text = fh.getvalue().decode('utf-8', errors='replace')
                    print(f"Preview:\n{text[:500]}...\n")
                except:
                    pass
                    
        except Exception as e:
            print(f"Error on {name}: {e}")
