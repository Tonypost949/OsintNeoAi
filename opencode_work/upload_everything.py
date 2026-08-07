"""
Full upload of opencode_work to Drive sharedall
Skips files > 200MB to avoid timeouts (large PPP exports already uploaded)
"""
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
MAX_SIZE = 200 * 1024 * 1024  # skip files over 200MB

creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
if not creds.valid:
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, "w") as t:
            t.write(creds.to_json())

drive = build("drive", "v3", credentials=creds)

def upload_file(local_path, name, folder_id):
    sz = local_path.stat().st_size
    if sz > MAX_SIZE:
        print(f"SKIP (too large {sz//1024//1024}MB): {name}")
        return None
    try:
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
        return resp.get("id")
    except Exception as e:
        print(f"ERROR {name}: {e}")
        return None

# --- TOP LEVEL FILES ---
print("\n=== UPLOADING TOP-LEVEL opencode_work ===")
top_files = list(WORK_DIR.glob("*"))
top_py   = [f for f in top_files if f.is_file() and f.suffix == ".py" and f.stat().st_size < MAX_SIZE]
top_csv  = [f for f in top_files if f.is_file() and f.suffix == ".csv" and f.stat().st_size < MAX_SIZE]
top_md   = [f for f in top_files if f.is_file() and f.suffix == ".md" and f.stat().st_size < MAX_SIZE]
top_sql  = [f for f in top_files if f.is_file() and f.suffix == ".sql" and f.stat().st_size < MAX_SIZE]
top_json = [f for f in top_files if f.is_file() and f.suffix == ".json" and f.stat().st_size < MAX_SIZE]
top_txt  = [f for f in top_files if f.is_file() and f.suffix == ".txt" and f.stat().st_size < MAX_SIZE]
top_zip  = [f for f in top_files if f.is_file() and f.suffix == ".zip" and f.stat().st_size < MAX_SIZE]
top_png  = [f for f in top_files if f.is_file() and f.suffix == ".png" and f.stat().st_size < MAX_SIZE]
top_db   = [f for f in top_files if f.is_file() and f.suffix == ".db" and f.stat().st_size < MAX_SIZE]
top_err  = [f for f in top_files if f.is_file() and f.suffix == ".err.log" and f.stat().st_size < MAX_SIZE]
top_out  = [f for f in top_files if f.is_file() and f.suffix == ".out.log" and f.stat().st_size < MAX_SIZE]
top_js   = [f for f in top_files if f.is_file() and f.suffix == ".js" and f.stat().st_size < MAX_SIZE]
top_html = [f for f in top_files if f.is_file() and f.suffix == ".html" and f.stat().st_size < MAX_SIZE]
top_ndjson = [f for f in top_files if f.is_file() and f.suffix == ".ndjson" and f.stat().st_size < MAX_SIZE]
top_manifest = [f for f in top_files if f.is_file() and f.suffix == ".manifest.txt" and f.stat().st_size < MAX_SIZE]

for cat, files in [
    ("Python", top_py), ("CSV", top_csv), ("Markdown", top_md), ("SQL", top_sql),
    ("JSON", top_json), ("Text", top_txt), ("ZIP", top_zip), ("PNG", top_png),
    ("DB", top_db), ("ErrLog", top_err), ("OutLog", top_out), ("JS", top_js),
    ("HTML", top_html), ("NDJSON", top_ndjson), ("Manifest", top_manifest)
]:
    if not files:
        continue
    print(f"\n--- {cat} ({len(files)} files) ---")
    for f in sorted(files):
        print(f"Uploading {f.name} ({f.stat().st_size//1024}KB)...")
        upload_file(f, f.name, FOLDER_ID)

# --- OSINT_VAULT_BACKUP ---
print("\n=== UPLOADING OSINT_VAULT_BACKUP ===")
vault = WORK_DIR / "OSINT_VAULT_BACKUP"
vault_files = [f for f in vault.glob("*") if f.is_file() and f.stat().st_size < MAX_SIZE]
print(f"--- Vault ({len(vault_files)} files) ---")
for f in sorted(vault_files):
    print(f"Uploading {f.name} ({f.stat().st_size//1024}KB)...")
    upload_file(f, f"V AULT_BACKUP/{f.name}", FOLDER_ID)

print("\n=== ALL DONE ===")
