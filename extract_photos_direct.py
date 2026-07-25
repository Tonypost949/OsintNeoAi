import zipfile, glob, json, os, subprocess

BASE_DIR = r"G:\OsintNeoAi"
PROJECT_ID = "project-743aab84-f9a5-4ec7-954"
DATASET_ID = "national_audits"
TABLE_ID = "google_photos_index"
OUT_JSONL = r"G:\OsintNeoAi\photos_extracted_hits.jsonl"

zips = glob.glob(os.path.join(BASE_DIR, "**", "*.zip"), recursive=True)
print(f"Inspecting {len(zips)} total zip archives in {BASE_DIR}...")

photo_records = []
for z in zips:
    try:
        with zipfile.ZipFile(z, 'r') as zf:
            for item in zf.namelist():
                if item.endswith('.json'):
                    try:
                        content = zf.read(item)
                        data = json.loads(content.decode('utf-8', errors='ignore'))
                        if isinstance(data, dict):
                            keys = set(data.keys())
                            if keys.intersection({"title", "photoTakenTime", "geoData", "creationTime"}):
                                row = {
                                    "title": data.get("title", ""),
                                    "description": data.get("description", ""),
                                    "photo_taken_time": data.get("photoTakenTime", {}).get("timestamp", ""),
                                    "geo_latitude": data.get("geoData", {}).get("latitude", 0.0),
                                    "geo_longitude": data.get("geoData", {}).get("longitude", 0.0),
                                    "geo_altitude": data.get("geoData", {}).get("altitude", 0.0),
                                    "url": data.get("url", ""),
                                    "filename": os.path.basename(item)
                                }
                                photo_records.append(row)
                    except Exception:
                        pass
    except Exception as e:
        print(f"Error reading zip {z}: {e}")

print(f"Extracted {len(photo_records)} total photo sidecar metadata records from zips.")

if photo_records:
    with open(OUT_JSONL, 'w', encoding='utf-8') as f:
        for rec in photo_records:
            f.write(json.dumps(rec) + '\n')
            
    print(f"Loading {len(photo_records)} photo records directly into BigQuery...")
    cmd = [
        "bq", "load",
        "--source_format=NEWLINE_DELIMITED_JSON",
        "--autodetect",
        f"{PROJECT_ID}:{DATASET_ID}.{TABLE_ID}",
        OUT_JSONL
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print("✅ Successfully loaded photo records into BigQuery!")
    else:
        print(f"❌ BigQuery load error: {res.stderr}")
