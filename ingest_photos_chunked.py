import os, sys, json, subprocess, zipfile, time
from pathlib import Path
from google.cloud import bigquery

PROJECT = "project-743aab84-f9a5-4ec7-954"
TABLE = f"{PROJECT}.national_audits.google_photos_index"
GDRIVE_PATH = "gdrive:Sharedall/takeouts all 22226"
WORK_DIR = Path(r"G:\OsintNeoAi\takeout_work")
PROGRESS_FILE = Path(r"C:\OsintNeoAi\takeout_photo_progress.json")
LOG_FILE = Path(r"C:\OsintNeoAi\takeout_ingest.log")

WORK_DIR.mkdir(parents=True, exist_ok=True)
client = bigquery.Client(project=PROJECT)

def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def load_progress():
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text())
    return {"completed_zips": [], "total_photos": 0, "errors": 0}

def save_progress(progress):
    PROGRESS_FILE.write_text(json.dumps(progress, indent=2))

def list_all_zips():
    result = subprocess.run(
        ["rclone", "ls", GDRIVE_PATH, "--include", "takeout-*.zip"],
        capture_output=True, text=True, timeout=300
    )
    zips = []
    for line in result.stdout.strip().split("\n"):
        if not line.strip():
            continue
        parts = line.strip().split(None, 1)
        if len(parts) == 2:
            size, name = int(parts[0]), parts[1]
            zips.append({"name": name, "size": size})
    zips.sort(key=lambda x: x["size"])
    return zips

def download_zip(zip_name):
    local_path = WORK_DIR / Path(zip_name).name
    if local_path.exists() and local_path.stat().st_size > 100:
        return local_path
    remote = f"{GDRIVE_PATH}/{zip_name}"
    subprocess.run(
        ["rclone", "copy", remote, str(WORK_DIR), "--no-traverse", "-P"],
        timeout=1800
    )
    if local_path.exists() and local_path.stat().st_size > 100:
        return local_path
    return None

def extract_photo_metadata(zip_path):
    photos = []
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for name in zf.namelist():
                if not name.lower().endswith('.json'):
                    continue
                if 'google photos' not in name.lower():
                    continue
                if name.endswith('print-subscriptions.json'):
                    continue
                if name.endswith('shared_album_comments.json'):
                    continue
                if name.endswith('user-generated-memory-titles.json'):
                    continue
                if name.endswith('assistant.json'):
                    continue
                if name.endswith('quality_preferences.json'):
                    continue
                if name.endswith('app_comments.json'):
                    continue
                if name.endswith('media_results.json'):
                    continue
                if name.endswith('sharing_stats.json'):
                    continue
                try:
                    data = json.loads(zf.read(name))
                except:
                    continue

                if not isinstance(data, dict):
                    continue
                if "photoTakenTime" not in data and "creationTime" not in data:
                    continue

                filename = data.get("title", Path(name).stem)
                creation = data.get("photoTakenTime", data.get("creationTime", {}))
                geo = data.get("geoData", {})
                camera_make = data.get("cameraMake", "")
                camera_model = data.get("cameraModel", "")

                photos.append({
                    "photo_id": f"{zip_path.stem}_{filename}",
                    "filename": filename,
                    "mime_type": _guess_mime(filename),
                    "creation_time": creation.get("formatted", ""),
                    "camera_make": camera_make,
                    "camera_model": camera_model,
                    "latitude": geo.get("latitude", 0.0),
                    "longitude": geo.get("longitude", 0.0),
                })
    except Exception as e:
        log(f"  ERROR reading zip: {e}")
    return photos

def _guess_mime(filename):
    ext = Path(filename).suffix.lower()
    return {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
        ".gif": "image/gif", ".heic": "image/heic", ".heif": "image/heif",
        ".mp4": "video/mp4", ".mov": "video/quicktime", ".webp": "image/webp",
        ".bmp": "image/bmp", ".raw": "image/raw", ".dng": "image/dng",
    }.get(ext, f"image/{ext.lstrip('.')}")

def load_to_bigquery(photos):
    if not photos:
        return 0
    import datetime
    rows = []
    for p in photos:
        rows.append({
            "photo_id": p["photo_id"],
            "filename": p["filename"],
            "mime_type": p["mime_type"],
            "creation_time": p["creation_time"],
            "camera_make": p["camera_make"],
            "camera_model": p["camera_model"],
            "focal_length": "",
            "aperture": "",
            "iso_equivalent": "",
            "ingest_timestamp": datetime.datetime.utcnow().isoformat(),
        })
    errors = client.insert_rows_json(TABLE, rows)
    return len(rows) - len(errors) if not errors else len(rows)

def main():
    progress = load_progress()
    completed = set(progress["completed_zips"])
    total_photos = progress["total_photos"]
    total_errors = progress.get("errors", 0)

    log(f"Resuming: {len(completed)} zips done, {total_photos} photos loaded")

    all_zips = list_all_zips()
    pending = [z for z in all_zips if z["name"] not in completed]
    pending = [z for z in pending if z["size"] >= 5 * 1024 * 1024]
    log(f"Total zips: {len(all_zips)}, Pending (>=5MB): {len(pending)}")

    chunk_size = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    chunk = pending[:chunk_size]

    for i, z in enumerate(chunk):
        log(f"[{i+1}/{len(chunk)}] {Path(z['name']).name} ({z['size']//1024//1024}MB)")
        try:
            zip_path = download_zip(z["name"])
            if not zip_path:
                log("  FAILED to download")
                total_errors += 1
                continue

            photos = extract_photo_metadata(zip_path)
            log(f"  Found {len(photos)} photo entries")

            if photos:
                loaded = load_to_bigquery(photos)
                total_photos += loaded
                log(f"  Loaded {loaded} to BigQuery")

            zip_path.unlink(missing_ok=True)
            completed.add(z["name"])
            progress["completed_zips"] = list(completed)
            progress["total_photos"] = total_photos
            progress["errors"] = total_errors
            save_progress(progress)
            log(f"  Total photos so far: {total_photos}")
        except Exception as e:
            log(f"  EXCEPTION: {e}")
            total_errors += 1
            progress["errors"] = total_errors
            save_progress(progress)

    log(f"\nCHUNK DONE. Photos: {total_photos}, Completed: {len(completed)}/{len(all_zips)}, Errors: {total_errors}")

if __name__ == "__main__":
    main()
