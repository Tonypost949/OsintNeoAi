import logging
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")
TOKEN_FILE = WORK_DIR / "OSINT_VAULT_BACKUP" / "token_drive_upload.json"
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
FOLDER_ID = "1q5bmZJQ9IuSudsie1KNuMWZ0mbfu6-gE"

creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
if not creds.valid:
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, "w") as t:
            t.write(creds.to_json())

drive = build("drive", "v3", credentials=creds)

FILES = [
    ("auto_join_schema.sql", WORK_DIR / "auto_join_schema.sql"),
    ("FOIA_BANC_OF_CALIFORNIA_MERCY_HOUSE.md", WORK_DIR / "FOIA_BANC_OF_CALIFORNIA_MERCY_HOUSE.md"),
    ("HUD_OIG_REFERRAL_MERCY_HOUSE.md", WORK_DIR / "HUD_OIG_REFERRAL_MERCY_HOUSE.md"),
    ("CPRA_ORANGE_COUNTY_RECORDS_REQUEST.md", WORK_DIR / "CPRA_ORANGE_COUNTY_RECORDS_REQUEST.md"),
    ("nppes_mercy_facilities.csv", WORK_DIR / "nppes_mercy_facilities.csv"),
    ("ppp_mercy_ca.csv", WORK_DIR / "ppp_mercy_ca.csv"),
    ("mercy_house_gsa_audit_2024.txt", WORK_DIR / "mercy_house_gsa_audit_2024.txt"),
    ("CHDO_MERCY_RICO_BREAKDOWN.md", WORK_DIR / "CHDO_MERCY_RICO_BREAKDOWN.md"),
    ("CANONICAL_BRIEFING_MERCY_HOUSE.md", WORK_DIR / "CANONICAL_BRIEFING_MERCY_HOUSE.md"),
    ("create_bq_tables.py", WORK_DIR / "create_bq_tables.py"),
    ("sos_pacep_search.py", WORK_DIR / "sos_pacep_search.py"),
]

for name, local_path in FILES:
    if not local_path.exists():
        print(f"SKIP (not found): {name}")
        continue
    sz = local_path.stat().st_size
    print(f"Uploading {name} ({sz:,} bytes)...")
    media = MediaFileUpload(str(local_path), chunksize=100*1024*1024, resumable=True)
    metadata = {"name": name, "parents": [FOLDER_ID]}
    req = drive.files().create(body=metadata, media_body=media, fields="id")
    resp = None
    while resp is None:
        try:
            status, resp = req.next_chunk()
            if status:
                print(f"  {int(status.progress()*100)}% done")
        except Exception as e:
            print(f"  Retry: {e}")
            import time; time.sleep(3)
            continue
    print(f"  Done: {resp.get('id')}")

print("\nAll uploads complete.")
