import os, sys, glob, json, subprocess

PROJECT_ID = "project-743aab84-f9a5-4ec7-954"
DATASET_ID = "national_audits"
TABLE_ID = "google_photos_index"
CHUNK_FILE = r"G:\OsintNeoAi\photos_takeout_hits.jsonl"

def main():
    if len(sys.argv) < 2:
        folder = r"G:\OsintNeoAi"
    else:
        folder = sys.argv[1]
        
    print(f"Scanning directory {folder}...")
    pattern = os.path.join(folder, "**", "*.json")
    files = glob.glob(pattern, recursive=True)
    print(f"Found {len(files)} total JSON files to inspect.")
    
    all_hits = []
    for f in files:
        if "photos_takeout_hits" in f or "chunk_progress" in f:
            continue
        try:
            with open(f, 'r', encoding='utf-8') as jf:
                data = json.load(jf)
                if isinstance(data, dict):
                    # Match any Google Photos JSON keys
                    keys = set(data.keys())
                    if keys.intersection({"title", "photoTakenTime", "geoData", "geoDataExif", "creationTime"}):
                        row = {
                            "title": data.get("title", ""),
                            "description": data.get("description", ""),
                            "photo_taken_time": data.get("photoTakenTime", {}).get("timestamp", ""),
                            "geo_latitude": data.get("geoData", {}).get("latitude", 0.0),
                            "geo_longitude": data.get("geoData", {}).get("longitude", 0.0),
                            "geo_altitude": data.get("geoData", {}).get("altitude", 0.0),
                            "url": data.get("url", ""),
                            "filename": os.path.basename(f)
                        }
                        all_hits.append(row)
        except Exception:
            pass
            
    print(f"Total Google Photos sidecar JSON hits found: {len(all_hits)}")
    if not all_hits:
        return
        
    with open(CHUNK_FILE, 'w', encoding='utf-8') as f:
        for hit in all_hits:
            f.write(json.dumps(hit) + '\n')
            
    print("Loading directly into BigQuery...")
    cmd = [
        "bq", "load",
        "--source_format=NEWLINE_DELIMITED_JSON",
        "--autodetect",
        f"{PROJECT_ID}:{DATASET_ID}.{TABLE_ID}",
        CHUNK_FILE
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"Successfully loaded {len(all_hits)} photo metadata records into BigQuery!")
    else:
        print(f"BigQuery Load Error: {res.stderr}")

if __name__ == "__main__":
    main()
