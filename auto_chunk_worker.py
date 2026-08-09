import subprocess, zipfile, json, os, glob, time

REMOTE_BASE = "gdrive:Sharedall/takeouts all 22226"
LOCAL_CHUNK_DIR = r"G:\OsintNeoAi\takeout_chunks"
EXTRACT_DIR = r"G:\OsintNeoAi\takeout_metadata_extracted"
TRACKER_PATH = r"G:\OsintNeoAi\chunk_progress_tracker.json"
PROJECT_ID = "project-743aab84-f9a5-4ec7-954"

os.makedirs(LOCAL_CHUNK_DIR, exist_ok=True)
os.makedirs(EXTRACT_DIR, exist_ok=True)

# Fetch zip list
res = subprocess.run(["rclone", "lsf", REMOTE_BASE, "--include", "*.zip"], capture_output=True, text=True)
zip_list = [f.strip() for f in res.stdout.splitlines() if f.strip().endswith('.zip')]
zip_list.sort()

# Load existing progress
completed = []
if os.path.exists(TRACKER_PATH):
    try:
        with open(TRACKER_PATH, 'r') as tf:
            data = json.load(tf)
            completed = data.get("completed_chunks", [])
    except Exception:
        pass

print(f"[WORKER] Total zip archives found: {len(zip_list)}. Completed so far: {len(completed)}")

for idx, zip_name in enumerate(zip_list):
    if zip_name in completed:
        continue
        
    print(f"\n[LOOP {idx+1}/{len(zip_list)}] Downloading {zip_name} to G:\\...")
    dl_cmd = [
        "rclone", "copy", f"{REMOTE_BASE}/{zip_name}", LOCAL_CHUNK_DIR,
        "--progress", "--retries", "15", "--low-level-retries", "30", "--drive-acknowledge-abuse"
    ]
    subprocess.run(dl_cmd)
    
    local_zip = os.path.join(LOCAL_CHUNK_DIR, zip_name)
    if os.path.exists(local_zip):
        print(f"[LOOP {idx+1}] Extracting metadata from {zip_name}...")
        extracted_count = 0
        try:
            with zipfile.ZipFile(local_zip, 'r') as zf:
                for item in zf.namelist():
                    if item.endswith('.json') or item.endswith('.csv') or item.endswith('.mbox'):
                        zf.extract(item, EXTRACT_DIR)
                        extracted_count += 1
            print(f"  -> Extracted {extracted_count} metadata files.")
        except Exception as e:
            print(f"  [ERROR] Extraction failed for {zip_name}: {e}")
            
        # Delete chunk immediately to keep disk clean
        os.remove(local_zip)
        print(f"[LOOP {idx+1}] Deleted local zip chunk {zip_name}")
        
        # Log completion to tracker
        completed.append(zip_name)
        tracker_data = {
            "total_zips": len(zip_list),
            "completed_chunks": completed,
            "current_index": idx + 1,
            "status": "RUNNING",
            "last_completed": zip_name,
            "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        with open(TRACKER_PATH, 'w') as tf:
            json.dump(tracker_data, tf, indent=2)
            
print("[WORKER] Sequential pipeline worker batch run finished!")
