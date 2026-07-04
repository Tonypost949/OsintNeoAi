import os
import io
import sys
import pypdf
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Reconfigure stdout to use UTF-8 just in case
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

file_id = "1VOP4Bl105W6zeQtpFzK4YpXhUDdtp7e5"
file_name = "andrew-do-forensic-audit-report-commissioned-by-county-phase-1.pdf"
output_dir = "./opencode_work/andrew_do_audit/"
output_path = os.path.join(output_dir, "phase1_forensic_audit_raw.txt")

print(f"Target file ID: {file_id}")
print(f"Target file name: {file_name}")

TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "token.json")
if not os.path.exists(TOKEN_FILE):
    print("Error: token.json not found in workspace.")
    sys.exit(1)

try:
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, ["https://www.googleapis.com/auth/drive.readonly"])
    service = build("drive", "v3", credentials=creds)
    
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, file_name)
    
    print("Downloading Weaver Forensic Audit Phase 1 PDF from Google Drive...")
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(f"Download progress: {int(status.progress() * 100)}%")
        
    with open(pdf_path, 'wb') as out_f:
        out_f.write(fh.getvalue())
    print("Download complete. Saved to: " + pdf_path)
    
    print("Parsing forensic audit report layers...")
    reader = pypdf.PdfReader(pdf_path)
    text_list = []
    total_pages = len(reader.pages)
    print(f"Total pages: {total_pages}")
    
    for idx, page in enumerate(reader.pages):
        page_text = page.extract_text() or ''
        text_list.append(f"--- PAGE {idx + 1} ---\n{page_text}")
        if (idx + 1) % 50 == 0:
            print(f"Processed {idx + 1}/{total_pages} pages")
            
    text = '\n\n'.join(text_list)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("Extraction complete. Saved to " + output_path)
    print(f"Total characters: {len(text)}")
    
    # Simple search verification
    print("\n--- Key Entities Scan ---")
    clinic_hits = 0
    media_hits = 0
    lines = text.split('\n')
    for line in lines:
        if '360 clinic' in line.lower():
            clinic_hits += 1
        if '2t media' in line.lower():
            media_hits += 1
            
    print(f"Found mentions of '360 Clinic': {clinic_hits}")
    print(f"Found mentions of '2T Media': {media_hits}")

except Exception as e:
    print(f"An error occurred: {e}")
