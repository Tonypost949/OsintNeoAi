import hashlib
import json
from pathlib import Path
from datetime import datetime

IMAGE_PATH = Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/evidence/screenshots/Ltbp9VGQsfDH_screenshot.png")
LOG_PATH = Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/data/staging/lightshot_Ltbp9VGQsfDH.json")

def hash_file(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

if IMAGE_PATH.exists():
    file_hash = hash_file(IMAGE_PATH)
    print(f"[+] Computed SHA-256: {file_hash}")
    
    # Save the ledger log for the autonomous enrichment engine
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    ledger_entry = {
        "source": "Lightshot (prnt.sc/Ltbp9VGQsfDH)",
        "file_id": "Ltbp9VGQsfDH",
        "relative_path": "evidence/screenshots/Ltbp9VGQsfDH_screenshot.png",
        "sha256_hash": file_hash,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "raw_content": "",
        "enrichment_status": "PENDING_AUTONOMOUS_REVIEW"
    }
    
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(ledger_entry, f, indent=2)
    print(f"[✓] Cryptographically sealed and queued in staging: {LOG_PATH}")
