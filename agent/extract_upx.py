from google.cloud import bigquery
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os
import io
import pypdf
from googleapiclient.http import MediaIoBaseDownload

file_id = "10LG02No0IXBs64ocMNgZKhog4wWO2lbh"
file_name = "Use Permit UPX1978058 - Supporting Documents.pdf"

print(f"--- Downloading and parsing {file_name} ---")

try:
    TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "token.json")
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, ["https://www.googleapis.com/auth/drive.readonly"])
        service = build("drive", "v3", credentials=creds)
        
        output_dir = './opencode_work/andrew_do_audit/'
        os.makedirs(output_dir, exist_ok=True)
        
        # Download PDF
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        
        # Save PDF temporarily
        pdf_path = os.path.join(output_dir, file_name)
        with open(pdf_path, 'wb') as out_f:
            out_f.write(fh.getvalue())
        
        print('Parsing forensic audit report layers...')
        try:
            reader = pypdf.PdfReader(pdf_path)
            text = '\n'.join([page.extract_text() or '' for page in reader.pages])
            output_path = os.path.join(output_dir, 'upx1978058_raw.txt')
            with open(output_path, 'w', encoding='utf-8') as txt_f:
                txt_f.write(text)
            print(f'✅ Extraction complete. Saved {len(text)} characters to {output_path}')
            
            # Check for 360 Clinic, 2T Media
            print("\n--- Scanning for intersections ---")
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if '360 clinic' in line.lower():
                    print(f"Found '360 Clinic' at line {i}: {line}")
                if '2t media' in line.lower():
                    print(f"Found '2T Media' at line {i}: {line}")
                if 'weaver' in line.lower() or 'andrew do' in line.lower():
                    print(f"Found target keyword at line {i}: {line}")
            
        except Exception as e:
            print(f"Error parsing PDF: {e}")
    else:
        print("No token.json found to download files.")

except Exception as e:
    print(f"Error: {e}")
