import zipfile, json, os, subprocess, sys

ZIP_PATH = r"G:\OsintNeoAi\takeout_chunks\takeout-20241120T035242Z-001.zip"
EXTRACT_DIR = r"G:\OsintNeoAi\takeout_metadata_extracted"
PROJECT_ID = "project-743aab84-f9a5-4ec7-954"

os.makedirs(EXTRACT_DIR, exist_ok=True)

with zipfile.ZipFile(ZIP_PATH, 'r') as zf:
    for item in zf.namelist():
        if item.endswith('History.json') or item.endswith('Addresses and more.json'):
            zf.extract(item, EXTRACT_DIR)
            print(f"Extracted: {item}")

history_path = os.path.join(EXTRACT_DIR, "Takeout", "Chrome", "History.json")
if os.path.exists(history_path):
    with open(history_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    history_entries = data.get("Browser History", [])
    print(f"Found {len(history_entries)} Chrome browsing history records.")
    
    ndjson_out = r"G:\OsintNeoAi\chrome_history.ndjson"
    with open(ndjson_out, 'w', encoding='utf-8') as f:
        for entry in history_entries:
            row = {
                "title": entry.get("title", ""),
                "url": entry.get("url", ""),
                "time_usec": entry.get("time_usec", 0),
                "page_transition": entry.get("page_transition", ""),
                "client_id": entry.get("client_id", "")
            }
            f.write(json.dumps(row) + '\n')
            
    cmd = [
        "bq", "load",
        "--source_format=NEWLINE_DELIMITED_JSON",
        "--autodetect",
        "--replace",
        f"{PROJECT_ID}:national_audits.takeout_chrome_history",
        ndjson_out
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    if res.returncode == 0:
        print(f"[SUCCESS] Loaded {len(history_entries)} Chrome history records directly to BigQuery!")
    else:
        print(f"[ERROR] BigQuery load failed: {res.stderr}")
