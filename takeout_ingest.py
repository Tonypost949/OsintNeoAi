"""
takeout_ingest.py — Full Google Takeout ingestion pipeline
Pulls from gdrive:Sharedall/takeouts all 22226, extracts, loads to BigQuery.

Usage:
    python takeout_ingest.py --download   # step 1: pull from Drive
    python takeout_ingest.py --extract    # step 2: unzip all
    python takeout_ingest.py --ingest     # step 3: push to BigQuery
    python takeout_ingest.py --all        # all three steps
"""

import os, sys, json, csv, zipfile, glob, subprocess, argparse
from pathlib import Path
from datetime import datetime

# === CONFIG ===
GDRIVE_PATH   = "gdrive:Sharedall/takeouts all 22226"
LOCAL_RAW     = r"C:\OsintNeoAi\takeout_raw"
LOCAL_EXTRACT = r"C:\OsintNeoAi\takeout_extracted"
BQ_PROJECT    = "project-743aab84-f9a5-4ec7-954"
BQ_DATASET    = "national_audits"

os.makedirs(LOCAL_RAW, exist_ok=True)
os.makedirs(LOCAL_EXTRACT, exist_ok=True)


# ─── STEP 1: DOWNLOAD ────────────────────────────────────────────────────────
def download_from_drive():
    print(f"\n[DOWNLOAD] Pulling from {GDRIVE_PATH} → {LOCAL_RAW}")
    cmd = [
        "rclone", "copy", GDRIVE_PATH, LOCAL_RAW,
        "--progress", "--transfers=4", "--checkers=8",
        "--drive-acknowledge-abuse"
    ]
    subprocess.run(cmd, check=True)
    zips = list(Path(LOCAL_RAW).rglob("*.zip"))
    print(f"[DOWNLOAD] Done. {len(zips)} zip files found.")
    return zips


# ─── STEP 2: EXTRACT ─────────────────────────────────────────────────────────
def extract_all():
    print(f"\n[EXTRACT] Extracting all zips in {LOCAL_RAW}")
    zips = list(Path(LOCAL_RAW).rglob("*.zip"))
    for z in zips:
        dest = Path(LOCAL_EXTRACT) / z.stem
        dest.mkdir(parents=True, exist_ok=True)
        print(f"  Extracting {z.name} → {dest}")
        try:
            with zipfile.ZipFile(z, 'r') as zf:
                zf.extractall(dest)
        except Exception as e:
            print(f"  [WARN] {z.name}: {e}")
    print(f"[EXTRACT] Done. Extracted {len(zips)} archives.")


# ─── STEP 3: INGEST TO BIGQUERY ──────────────────────────────────────────────
def bq_load(table_id, json_path):
    """Load a newline-delimited JSON file into BigQuery (auto-detect schema)."""
    full_table = f"{BQ_PROJECT}:{BQ_DATASET}.{table_id}"
    cmd = [
        "bq", "load",
        "--source_format=NEWLINE_DELIMITED_JSON",
        "--autodetect",
        "--replace",
        full_table,
        json_path
    ]
    print(f"  → bq load {full_table}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  [ERROR] {result.stderr.strip()}")
    else:
        print(f"  [OK] Loaded {table_id}")


def parse_chrome_history():
    """Parse Chrome BrowserHistory.json → NDJSON for BQ."""
    out_path = os.path.join(LOCAL_EXTRACT, "_bq_chrome_history.ndjson")
    files = list(Path(LOCAL_EXTRACT).rglob("BrowserHistory.json"))
    rows = []
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8", errors="replace"))
            for item in data.get("Browser History", []):
                rows.append({
                    "title": item.get("title",""),
                    "url": item.get("url",""),
                    "time_usec": item.get("time_usec", 0),
                    "visit_time": str(datetime.utcfromtimestamp(
                        (item.get("time_usec",0) - 11644473600000000) / 1e6
                    )) if item.get("time_usec") else None,
                    "transition": item.get("page_transition",""),
                    "source_file": str(f)
                })
        except Exception as e:
            print(f"  [WARN] Chrome parse error {f}: {e}")
    with open(out_path, "w", encoding="utf-8") as fout:
        for r in rows:
            fout.write(json.dumps(r) + "\n")
    print(f"  Chrome history: {len(rows):,} rows → {out_path}")
    return out_path, len(rows)


def parse_photos_metadata():
    """Parse Google Photos JSON sidecar files → NDJSON."""
    out_path = os.path.join(LOCAL_EXTRACT, "_bq_photos_index.ndjson")
    # Photos metadata files end in .json but are NOT BrowserHistory
    files = list(Path(LOCAL_EXTRACT).rglob("*.json"))
    rows = []
    for f in files:
        if f.name.startswith("_bq_"):
            continue
        if "Photos" not in str(f) and "photo" not in f.name.lower():
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8", errors="replace"))
            if "title" in data and ("geoData" in data or "photoTakenTime" in data):
                rows.append({
                    "title": data.get("title",""),
                    "description": data.get("description",""),
                    "photo_taken_time": data.get("photoTakenTime", {}).get("formatted",""),
                    "photo_taken_ts": data.get("photoTakenTime", {}).get("timestamp",""),
                    "lat": data.get("geoData", {}).get("latitude", None),
                    "lng": data.get("geoData", {}).get("longitude", None),
                    "altitude": data.get("geoData", {}).get("altitude", None),
                    "url": data.get("url",""),
                    "google_photos_origin": str(data.get("googlePhotosOrigin",{})),
                    "source_file": str(f)
                })
        except Exception:
            pass
    with open(out_path, "w", encoding="utf-8") as fout:
        for r in rows:
            fout.write(json.dumps(r) + "\n")
    print(f"  Photos metadata: {len(rows):,} rows → {out_path}")
    return out_path, len(rows)


def parse_drive_index():
    """Index all files found in Drive takeout."""
    out_path = os.path.join(LOCAL_EXTRACT, "_bq_drive_index.ndjson")
    all_files = list(Path(LOCAL_EXTRACT).rglob("*"))
    rows = []
    for f in all_files:
        if f.is_file() and not f.name.startswith("_bq_"):
            rows.append({
                "filename": f.name,
                "extension": f.suffix.lower(),
                "full_local_path": str(f),
                "size_bytes": f.stat().st_size,
                "modified": datetime.utcfromtimestamp(f.stat().st_mtime).isoformat(),
                "relative_path": str(f.relative_to(LOCAL_EXTRACT))
            })
    with open(out_path, "w", encoding="utf-8") as fout:
        for r in rows:
            fout.write(json.dumps(r) + "\n")
    print(f"  Drive file index: {len(rows):,} rows → {out_path}")
    return out_path, len(rows)


def parse_location_history():
    """Parse location history Records.json."""
    out_path = os.path.join(LOCAL_EXTRACT, "_bq_location_history.ndjson")
    files = list(Path(LOCAL_EXTRACT).rglob("Records.json"))
    rows = []
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8", errors="replace"))
            for loc in data.get("locations", []):
                rows.append({
                    "timestamp_ms": loc.get("timestampMs", loc.get("timestamp","")),
                    "lat": loc.get("latitudeE7", 0) / 1e7,
                    "lng": loc.get("longitudeE7", 0) / 1e7,
                    "accuracy": loc.get("accuracy", None),
                    "altitude": loc.get("altitude", None),
                    "velocity": loc.get("velocity", None),
                    "heading": loc.get("heading", None),
                    "source_file": str(f)
                })
        except Exception as e:
            print(f"  [WARN] Location parse error {f}: {e}")
    with open(out_path, "w", encoding="utf-8") as fout:
        for r in rows:
            fout.write(json.dumps(r) + "\n")
    print(f"  Location history: {len(rows):,} rows → {out_path}")
    return out_path, len(rows)


def ingest_to_bq():
    print(f"\n[INGEST] Parsing and loading to BigQuery ({BQ_PROJECT}.{BQ_DATASET})")

    chrome_path, chrome_rows = parse_chrome_history()
    if chrome_rows > 0:
        bq_load("takeout_chrome_history", chrome_path)

    photos_path, photos_rows = parse_photos_metadata()
    if photos_rows > 0:
        bq_load("google_photos_index", photos_path)

    drive_path, drive_rows = parse_drive_index()
    if drive_rows > 0:
        bq_load("drive_file_index", drive_path)

    loc_path, loc_rows = parse_location_history()
    if loc_rows > 0:
        bq_load("takeout_location_history", loc_path)

    print(f"\n[INGEST] Complete.")
    print(f"  Chrome: {chrome_rows:,} rows")
    print(f"  Photos: {photos_rows:,} rows")
    print(f"  Drive:  {drive_rows:,} rows")
    print(f"  Location: {loc_rows:,} rows")


# ─── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--extract",  action="store_true")
    parser.add_argument("--ingest",   action="store_true")
    parser.add_argument("--all",      action="store_true")
    args = parser.parse_args()

    if args.all or args.download:
        download_from_drive()
    if args.all or args.extract:
        extract_all()
    if args.all or args.ingest:
        ingest_to_bq()

    if not any(vars(args).values()):
        print("Usage: python takeout_ingest.py --all")
        print("       python takeout_ingest.py --download --extract --ingest")
