import zipfile, json, os, subprocess

ZIP_PATH = r"G:\OsintNeoAi\takeout_chunks\takeout-20241120T041851Z-001.zip"
EXTRACT_DIR = r"G:\OsintNeoAi\takeout_metadata_extracted"
PROJECT_ID = "project-743aab84-f9a5-4ec7-954"

os.makedirs(EXTRACT_DIR, exist_ok=True)

with zipfile.ZipFile(ZIP_PATH, 'r') as zf:
    entries = zf.namelist()
    print(f"[CHUNK 2] Total files in zip: {len(entries)}")
    for item in entries:
        print(f"  -> {item}")
        if item.endswith('.json') or item.endswith('.csv') or item.endswith('.mbox'):
            zf.extract(item, EXTRACT_DIR)

# Update tracking file
tracker_path = r"G:\OsintNeoAi\chunk_progress_tracker.json"
tracker_data = {
    "total_zips": 1620,
    "completed_chunks": ["takeout-20241120T035242Z-001.zip", "takeout-20241120T041851Z-001.zip"],
    "current_batch": 2,
    "status": "CHUNK_2_COMPLETED",
    "last_updated": os.path.basename(ZIP_PATH)
}
with open(tracker_path, 'w') as tf:
    json.dump(tracker_data, tf, indent=2)

print("[CHUNK 2] Completed and logged to tracker!")
