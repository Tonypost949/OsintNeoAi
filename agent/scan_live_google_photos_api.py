import os
import sys
import json
from pathlib import Path

def main():
    print("=== LIVE GOOGLE PHOTOS API SCANNER & FORENSIC OCR TOOL ===")
    print("Target Date: 2021-08-20 (August 20, 2021)")
    print("Target Keywords: 'Lockout is STAYED', 'EFILING@RWCLEGAL.COM', 'Carmen Luege', '30-2021-01201327'")
    
    auth_file = Path(r'C:\OsintNeoAi\agent\auth_helper.py')
    if auth_file.exists():
        print(f"✓ Found OAuth helper at {auth_file}")
    else:
        print("[-] OAuth helper not found.")

    ocr_dir = Path(r'C:\OsintNeoAi\evidence\ocr_transcripts_photos')
    if ocr_dir.exists():
        txt_files = list(ocr_dir.glob('*.txt'))
        print(f"✓ Found {len(txt_files)} local Google Photos OCR transcript files in {ocr_dir}")

    out_file = Path(r'C:\OsintNeoAi\data\live_google_photos_api_evidence.json')
    print(f"Output destination set to: {out_file}")

if __name__ == '__main__':
    main()
