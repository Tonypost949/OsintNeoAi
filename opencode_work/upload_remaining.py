"""Upload remaining missing files to Drive"""
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

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

def upload_file(local_path, name, folder_id):
    sz = local_path.stat().st_size
    print(f"Uploading {name} ({sz//1024}KB)...")
    try:
        from googleapiclient.http import MediaFileUpload
        media = MediaFileUpload(str(local_path), chunksize=100*1024*1024, resumable=True)
        metadata = {"name": name, "parents": [folder_id]}
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
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

# 1. Evidence PNGs (mercy house pages)
png_dir = WORK_DIR
png_files = sorted(png_dir.glob("mercy_house_page_*.png"))
print(f"\n=== MERCY HOUSE EVIDENCE PAGES ({len(png_files)} files) ===")
for f in png_files:
    upload_file(f, f"EVIDENCE_PAGES/{f.name}", FOLDER_ID)

# 2. Error/out logs
print("\n=== LOGS ===")
for f in sorted(WORK_DIR.glob("*.err.log")):
    upload_file(f, f"LOGS/{f.name}", FOLDER_ID)
for f in sorted(WORK_DIR.glob("*.out.log")):
    upload_file(f, f"LOGS/{f.name}", FOLDER_ID)

# 3. DB files
print("\n=== DB FILES ===")
for f in sorted(WORK_DIR.glob("*.db")):
    upload_file(f, f"DB/{f.name}", FOLDER_ID)

# 4. JS/HTML
print("\n=== JS/HTML ===")
for f in sorted(WORK_DIR.glob("*.js")):
    upload_file(f, f"JS/{f.name}", FOLDER_ID)
for f in sorted(WORK_DIR.glob("*.html")):
    upload_file(f, f"HTML/{f.name}", FOLDER_ID)

# 5. NDJSON
print("\n=== NDJSON ===")
for f in sorted(WORK_DIR.glob("*.ndjson")):
    upload_file(f, f"NDJSON/{f.name}", FOLDER_ID)

# 6. GCS chunk file
print("\n=== GCS CHUNK ===")
chunk = WORK_DIR / "chunk_004.dat"
if chunk.exists():
    upload_file(chunk, f"GCS_CHUNKS/chunk_004.dat", FOLDER_ID)

# 7. OSINT_VAULT_BACKUP remaining files
print("\n=== OSINT_VAULT_BACKUP remaining ===")
vault = WORK_DIR / "OSINT_VAULT_BACKUP"
vault_all = set(f.name for f in vault.glob("*") if f.is_file())
already_uploaded = {
    "OSINT_VAULT_BACKUP.zip", "Makaveli_Conversation_Log.jsonl",
    "master_index.db", "token_drive_upload.json", "token_send.json",
    "client_secret.json", "token.json.stale", ".gitignore",
    "osint-agent.code-workspace"
}
skip_these_large = {
    "HBNC_Criminal_Referral_Evidence_Pack_20260619_211612.zip",
    "HBNC_Criminal_Referral_Evidence_Pack_20260619_211630.zip",
    "HBNC_Criminal_Referral_Evidence_Pack_20260617_161638.zip",
}
for f in sorted(vault.glob("*")):
    if not f.is_file():
        continue
    if f.name in already_uploaded or f.name in skip_these_large:
        print(f"SKIP (already there or too large): {f.name}")
        continue
    if f.stat().st_size > 200*1024*1024:
        print(f"SKIP (too large {f.stat().st_size//1024//1024}MB): {f.name}")
        continue
    upload_file(f, f"V AULT_BACKUP/{f.name}", FOLDER_ID)

print("\n=== ALL DONE ===")
