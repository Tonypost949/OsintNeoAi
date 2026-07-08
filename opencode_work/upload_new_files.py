import os, pickle, io
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
TOKEN_PATH = Path("C:/Users/HP/OneDrive/Documents/opencode_work/OSINT_VAULT_BACKUP/drive_token.pkl")
UPLOAD_FOLDER_ID = "1q5bmZJQ9IuSudsie1KNuMWZ0mbfu6-gE"
WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")

creds = Credentials.from_authorized_user_info(info={})
flow = InstalledAppFlow.from_client_secrets_file(
    str(WORK_DIR / "OSINT_VAULT_BACKUP" / "credentials.json"), SCOPES
)
creds = flow.run_local_server(port=0)
with open(TOKEN_PATH, "wb") as f:
    pickle.dump(creds, f)

drive = build("drive", "v3", credentials=creds)

FILES_TO_UPLOAD = [
    UPLOAD_FOLDER_ID + "/auto_join_schema.sql",
    UPLOAD_FOLDER_ID + "/FOIA_BANC_OF_CALIFORNIA_MERCY_HOUSE.md",
    UPLOAD_FOLDER_ID + "/HUD_OIG_REFERRAL_MERCY_HOUSE.md",
    UPLOAD_FOLDER_ID + "/CPRA_ORANGE_COUNTY_RECORDS_REQUEST.md",
    UPLOAD_FOLDER_ID + "/nppes_mercy_facilities.csv",
    UPLOAD_FOLDER_ID + "/ppp_mercy_ca.csv",
    UPLOAD_FOLDER_ID + "/mercy_house_gsa_audit_2024.txt",
    UPLOAD_FOLDER_ID + "/CHDO_MERCY_RICO_BREAKDOWN.md",
    UPLOAD_FOLDER_ID + "/CANONICAL_BRIEFING_MERCY_HOUSE.md",
    UPLOAD_FOLDER_ID + "/sos_pacep_search.py",
    UPLOAD_FOLDER_ID + "/create_bq_tables.py",
]

# Actually map to local paths
LOCAL_FILES = {
    "auto_join_schema.sql": WORK_DIR / "auto_join_schema.sql",
    "FOIA_BANC_OF_CALIFORNIA_MERCY_HOUSE.md": WORK_DIR / "FOIA_BANC_OF_CALIFORNIA_MERCY_HOUSE.md",
    "HUD_OIG_REFERRAL_MERCY_HOUSE.md": WORK_DIR / "HUD_OIG_REFERRAL_MERCY_HOUSE.md",
    "CPRA_ORANGE_COUNTY_RECORDS_REQUEST.md": WORK_DIR / "CPRA_ORANGE_COUNTY_RECORDS_REQUEST.md",
    "nppes_mercy_facilities.csv": WORK_DIR / "nppes_mercy_facilities.csv",
    "ppp_mercy_ca.csv": WORK_DIR / "ppp_mercy_ca.csv",
    "mercy_house_gsa_audit_2024.txt": WORK_DIR / "mercy_house_gsa_audit_2024.txt",
    "CHDO_MERCY_RICO_BREAKDOWN.md": WORK_DIR / "CHDO_MERCY_RICO_BREAKDOWN.md",
    "CANONICAL_BRIEFING_MERCY_HOUSE.md": WORK_DIR / "CANONICAL_BRIEFING_MERCY_HOUSE.md",
    "sos_pacep_search.py": WORK_DIR / "sos_pacep_search.py",
    "create_bq_tables.py": WORK_DIR / "create_bq_tables.py",
}

for name, local_path in LOCAL_FILES.items():
    if not local_path.exists():
        print(f"SKIP (not found): {name}")
        continue
    file_size = local_path.stat().st_size
    print(f"Uploading {name} ({file_size:,} bytes)...")
    media = MediaFileUpload(str(local_path), resumable=True)
    metadata = {"name": name, "parents": [UPLOAD_FOLDER_ID]}
    req = drive.files().create(body=metadata, media_body=media, fields="id")
    status, done = req.next_chunk()
    while not done:
        status, done = req.next_chunk()
    print(f"  -> Done: {status}")
print("\nAll uploads complete.")
