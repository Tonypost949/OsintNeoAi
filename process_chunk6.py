import zipfile, json, os

ZIP_PATH = r"G:\OsintNeoAi\takeout_chunks\takeout-20250315T090934Z-001.zip"
EXTRACT_DIR = r"G:\OsintNeoAi\takeout_metadata_extracted"

os.makedirs(EXTRACT_DIR, exist_ok=True)

if os.path.exists(ZIP_PATH):
    print("[CHUNK 6] Extracting files...")
    with zipfile.ZipFile(ZIP_PATH, 'r') as zf:
        entries = zf.namelist()
        print(f"[CHUNK 6] Total entries: {len(entries)}")
        for item in entries:
            if item.endswith('.json') or item.endswith('.csv') or item.endswith('.mbox'):
                zf.extract(item, EXTRACT_DIR)
                print(f"  -> Extracted: {item}")

# Update progress tracker
tracker_path = r"G:\OsintNeoAi\chunk_progress_tracker.json"
tracker_data = {
    "total_zips": 1620,
    "completed_chunks": [
        "takeout-20241120T035242Z-001.zip",
        "takeout-20241120T041851Z-001.zip",
        "takeout-20241121T010253Z-001.zip",
        "takeout-20250115T152414Z-001.zip",
        "takeout-20250311T090934Z-001.zip",
        "takeout-20250315T090934Z-001.zip"
    ],
    "current_batch": 6,
    "status": "CHUNK_6_COMPLETED"
}
with open(tracker_path, 'w') as tf:
    json.dump(tracker_data, tf, indent=2)

print("[CHUNK 6] Completed and updated chunk_progress_tracker.json!")
