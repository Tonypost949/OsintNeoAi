import subprocess
import zipfile
import json
import os
import glob
import time

REMOTE_BASE = "gdrive:Sharedall/takeouts all 22226"
LOCAL_CHUNK_DIR = r"C:\OsintNeoAi\data\takeout_chunks_tmp"
EXTRACT_DIR = r"C:\OsintNeoAi\data\takeout_metadata_extracted"
PROJECT_ID = "noble-beanbag-497411-m4"

os.makedirs(LOCAL_CHUNK_DIR, exist_ok=True)
os.makedirs(EXTRACT_DIR, exist_ok=True)

def process_takeouts():
    print("[BATCH RUNNER v2] Fetching list of Takeout zip files from Google Drive...")
    res = subprocess.run(["rclone", "lsf", REMOTE_BASE, "--include", "*.zip"], capture_output=True, text=True)
    zip_list = [f.strip() for f in res.stdout.splitlines() if f.strip().endswith('.zip')]
    zip_list.sort()

    print(f"[BATCH RUNNER v2] Found total {len(zip_list)} zip chunks in Drive.")

    BATCH_SIZE = 3

    for i in range(0, len(zip_list), BATCH_SIZE):
        batch = zip_list[i:i+BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        total_batches = (len(zip_list) + BATCH_SIZE - 1) // BATCH_SIZE

        print(f"\n==========================================")
        print(f"[BATCH {batch_num}/{total_batches}] Downloading & Processing: {batch}")
        print(f"==========================================")

        for zip_name in batch:
            print(f"[DOWNLOADING] {zip_name} -> {LOCAL_CHUNK_DIR}")
            dl_cmd = [
                "rclone", "copy", f"{REMOTE_BASE}/{zip_name}", LOCAL_CHUNK_DIR,
                "--progress", "--retries", "10", "--low-level-retries", "20", "--drive-acknowledge-abuse"
            ]
            subprocess.run(dl_cmd)

            local_zip_path = os.path.join(LOCAL_CHUNK_DIR, zip_name)
            if os.path.exists(local_zip_path):
                print(f"[EXTRACTING FORENSIC TARGETS] {zip_name}...")
                try:
                    with zipfile.ZipFile(local_zip_path, 'r') as zf:
                        for item in zf.namelist():
                            lower_name = item.lower()
                            if any(ext in lower_name for ext in ['.json', '.csv', '.mbox', '.vcf', 'bookmarks.html', 'records.json', 'location history']):
                                zf.extract(item, EXTRACT_DIR)
                                print(f"  -> Extracted: {item}")
                except Exception as e:
                    print(f"  [ERROR] Failed to extract {zip_name}: {e}")

                # Immediate cleanup of heavy zip to strictly conserve local disk space
                try:
                    os.remove(local_zip_path)
                    print(f"[CLEANUP] Deleted raw zip {zip_name} to preserve disk space.")
                except Exception as e:
                    print(f"[WARNING] Could not delete {local_zip_path}: {e}")

    print("\n[BATCH RUNNER v2] ALL TAKEOUT CHUNKS PROCESSED AND CLEANED!")

if __name__ == "__main__":
    process_takeouts()
