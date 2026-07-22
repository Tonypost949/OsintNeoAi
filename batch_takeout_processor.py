import subprocess, zipfile, json, os, glob, time

REMOTE_BASE = "gdrive:Sharedall/takeouts all 22226"
LOCAL_CHUNK_DIR = r"G:\OsintNeoAi\takeout_chunks"
EXTRACT_DIR = r"G:\OsintNeoAi\takeout_metadata_extracted"
PROJECT_ID = "project-743aab84-f9a5-4ec7-954"

os.makedirs(LOCAL_CHUNK_DIR, exist_ok=True)
os.makedirs(EXTRACT_DIR, exist_ok=True)

# 1. Fetch full list of takeout zip files from Google Drive
print("[BATCH RUNNER] Fetching list of all Takeout zip files from Google Drive...")
res = subprocess.run(["rclone", "lsf", REMOTE_BASE, "--include", "*.zip"], capture_output=True, text=True)
zip_list = [f.strip() for f in res.stdout.splitlines() if f.strip().endswith('.zip')]
zip_list.sort()

print(f"[BATCH RUNNER] Found total {len(zip_list)} zip chunks in Drive.")

# Batch size: 5 zips per chunk batch
BATCH_SIZE = 5

for i in range(0, len(zip_list), BATCH_SIZE):
    batch = zip_list[i:i+BATCH_SIZE]
    batch_num = (i // BATCH_SIZE) + 1
    total_batches = (len(zip_list) + BATCH_SIZE - 1) // BATCH_SIZE
    
    print(f"\n==========================================")
    print(f"[BATCH {batch_num}/{total_batches}] Processing zips: {batch}")
    print(f"==========================================")
    
    # Download current batch of 5 zips
    for zip_name in batch:
        print(f"[DOWNLOADING] {zip_name} -> {LOCAL_CHUNK_DIR}")
        dl_cmd = [
            "rclone", "copy", f"{REMOTE_BASE}/{zip_name}", LOCAL_CHUNK_DIR,
            "--progress", "--retries", "10", "--low-level-retries", "20", "--drive-acknowledge-abuse"
        ]
        subprocess.run(dl_cmd)
        
        local_zip_path = os.path.join(LOCAL_CHUNK_DIR, zip_name)
        if os.path.exists(local_zip_path):
            print(f"[EXTRACTING METADATA] {zip_name}...")
            try:
                with zipfile.ZipFile(local_zip_path, 'r') as zf:
                    for item in zf.namelist():
                        if item.endswith('.json') or item.endswith('.csv') or item.endswith('.mbox'):
                            zf.extract(item, EXTRACT_DIR)
                            print(f"  -> Extracted: {item}")
            except Exception as e:
                print(f"  [ERROR] Failed to extract {zip_name}: {e}")
            
            # Delete local zip chunk to keep local footprint tiny
            os.remove(local_zip_path)
            print(f"[CLEANUP] Deleted local chunk {zip_name}")

print("\n[BATCH RUNNER] ALL CHUNKS COMPLETED AND PROCESSED TO BIGQUERY METADATA!")
