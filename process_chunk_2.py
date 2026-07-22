import zipfile, json, os, subprocess

REMOTE_FILE = "gdrive:Sharedall/takeouts all 22226/takeout-20241120T041851Z-001.zip"
LOCAL_CHUNK_DIR = r"G:\OsintNeoAi\takeout_chunks"
EXTRACT_DIR = r"G:\OsintNeoAi\takeout_metadata_extracted"
PROJECT_ID = "project-743aab84-f9a5-4ec7-954"

os.makedirs(LOCAL_CHUNK_DIR, exist_ok=True)
os.makedirs(EXTRACT_DIR, exist_ok=True)

print("[CHUNK 2] Downloading takeout-20241120T041851Z-001.zip to G:\\...")
cmd_dl = [
    "rclone", "copy", REMOTE_FILE, LOCAL_CHUNK_DIR,
    "--progress", "--drive-acknowledge-abuse"
]
subprocess.run(cmd_dl)

zip_path = os.path.join(LOCAL_CHUNK_DIR, "takeout-20241120T041851Z-001.zip")
if os.path.exists(zip_path):
    print("[CHUNK 2] Extracting metadata files...")
    with zipfile.ZipFile(zip_path, 'r') as zf:
        for item in zf.namelist():
            if item.endswith('.json') or item.endswith('.csv') or item.endswith('.mbox'):
                zf.extract(item, EXTRACT_DIR)
                print(f"  -> Extracted: {item}")
                
    # Update tracker
    tracker_path = r"G:\OsintNeoAi\chunk_progress_tracker.json"
    tracker_data = {"completed_chunks": ["takeout-20241120T035242Z-001.zip", "takeout-20241120T041851Z-001.zip"], "status": "IN_PROGRESS"}
    with open(tracker_path, 'w') as tf:
        json.dump(tracker_data, tf, indent=2)
    print("[CHUNK 2] Updated chunk_progress_tracker.json!")
