import os
import sys
import json
import time
import datetime
import subprocess
import zipfile
import io
from google.cloud import bigquery
from google.api_core.exceptions import Conflict

sys.stdout.reconfigure(encoding="utf-8")

GCP_PROJECT = os.environ.get("GOOGLE_PROJECT_ID", "project-743aab84-f9a5-4ec7-954")
BQ_DATASET = "national_audits"
TABLE_NAME = "takeout_photos_metadata"
FULL_TABLE_ID = f"{GCP_PROJECT}.{BQ_DATASET}.{TABLE_NAME}"
MANIFEST_FILE = "C:\\OsintNeoAi\\photo_zip_list.json"

class RemoteZipStream(io.RawIOBase):
    def __init__(self, remote_path):
        self.remote_path = remote_path
        self.offset = 0
        cmd = [
            "rclone", "size", remote_path, "--json",
            "--retries", "10", "--low-level-retries", "10", "--retries-sleep", "3s"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        info = json.loads(res.stdout)
        self.size = info["bytes"]

    def seekable(self):
        return True

    def seek(self, offset, whence=io.SEEK_SET):
        if whence == io.SEEK_SET:
            self.offset = offset
        elif whence == io.SEEK_CUR:
            self.offset += offset
        elif whence == io.SEEK_END:
            self.offset = self.size + offset
        return self.offset

    def tell(self):
        return self.offset

    def readinto(self, b):
        if self.offset >= self.size:
            return 0
        count = min(len(b), self.size - self.offset)
        cmd = [
            "rclone", "cat", self.remote_path,
            "--offset", str(self.offset),
            "--count", str(count),
            "--retries", "10", "--low-level-retries", "10", "--retries-sleep", "3s"
        ]
        
        for attempt in range(1, 6):
            try:
                res = subprocess.run(cmd, capture_output=True, check=True)
                data = res.stdout
                b[:len(data)] = data
                self.offset += len(data)
                return len(data)
            except Exception as e:
                if attempt == 5:
                    raise e
                time.sleep(2)
        return 0

def ensure_table(bq_client):
    schema = [
        bigquery.SchemaField("photo_name", "STRING"),
        bigquery.SchemaField("photo_timestamp", "TIMESTAMP"),
        bigquery.SchemaField("latitude", "FLOAT64"),
        bigquery.SchemaField("longitude", "FLOAT64"),
        bigquery.SchemaField("altitude", "FLOAT64"),
        bigquery.SchemaField("camera_make", "STRING"),
        bigquery.SchemaField("camera_model", "STRING"),
        bigquery.SchemaField("description", "STRING"),
        bigquery.SchemaField("zip_source", "STRING"),
        bigquery.SchemaField("inner_path", "STRING")
    ]
    try:
        bq_client.get_table(FULL_TABLE_ID)
        print(f"[BQ] Table {FULL_TABLE_ID} already exists.")
    except Exception:
        try:
            table = bigquery.Table(FULL_TABLE_ID, schema=schema)
            bq_client.create_table(table)
            print(f"[BQ] Created table {FULL_TABLE_ID}.")
        except Conflict:
            print(f"[BQ] Table {FULL_TABLE_ID} already exists.")

def load_photo_zips():
    if os.path.exists(MANIFEST_FILE):
        with open(MANIFEST_FILE, "r") as f:
            zips = json.load(f)
            print(f"[MANIFEST] Loaded {len(zips)} photo ZIP files from cache.")
            return zips
    else:
        cmd = ["rclone", "lsf", "gdrive:Sharedall/takeouts all 22226/", "--include", "*.zip", "--retries", "10"]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        files = [f.strip() for f in res.stdout.splitlines() if f.strip().endswith(".zip")]
        return [f for f in files if "20240116" in f or "20250408" in f or "202411" in f]

def process_remote_zip(bq_client, zip_name):
    # Determine remote path
    if "/" in zip_name:
        remote_path = f"gdrive:Sharedall/takeouts all 22226/{zip_name}"
    else:
        remote_path = f"gdrive:Sharedall/takeouts all 22226/{zip_name}"
        
    print(f"\n[STREAM] Opening remote ZIP {zip_name} via byte-range streaming...")
    rows = []
    
    try:
        rstream = RemoteZipStream(remote_path)
        with zipfile.ZipFile(rstream) as z:
            for file_info in z.infolist():
                if file_info.filename.endswith(".json") and "Google Photos" in file_info.filename:
                    try:
                        with z.open(file_info) as f:
                            data = json.load(f)
                            title = data.get("title", "")
                            desc = data.get("description", "")
                            
                            photo_ts = None
                            taken_time = data.get("photoTakenTime", {})
                            ts_sec = taken_time.get("timestamp")
                            if ts_sec:
                                try:
                                    photo_ts = datetime.datetime.utcfromtimestamp(int(ts_sec)).isoformat() + "Z"
                                except Exception:
                                    pass
                                    
                            geo = data.get("geoData", {}) or data.get("geoDataExif", {})
                            lat = geo.get("latitude")
                            lon = geo.get("longitude")
                            alt = geo.get("altitude")
                            
                            if lat == 0.0 and lon == 0.0:
                                lat, lon, alt = None, None, None
                                
                            row = {
                                "photo_name": title,
                                "photo_timestamp": photo_ts,
                                "latitude": lat,
                                "longitude": lon,
                                "altitude": alt,
                                "camera_make": None,
                                "camera_model": None,
                                "description": desc,
                                "zip_source": zip_name,
                                "inner_path": file_info.filename
                            }
                            rows.append(row)
                    except Exception:
                        pass
    except Exception as e:
        print(f"[ERROR] Streaming zip {zip_name}: {e}")
        return 0

    if rows:
        print(f"[BQ] Streaming load of {len(rows)} photo sidecars into BigQuery...")
        job_config = bigquery.LoadJobConfig(write_disposition=bigquery.WriteDisposition.WRITE_APPEND)
        job = bq_client.load_table_from_json(rows, FULL_TABLE_ID, job_config=job_config)
        job.result()
        print(f"[✓] Successfully loaded {len(rows)} photo records from {zip_name}!")
        return len(rows)
    else:
        print(f"[BQ] No photo sidecar JSONs found in {zip_name}.")
        return 0

def main():
    print("[PIPELINE] Initializing BigQuery client...")
    bq_client = bigquery.Client(project=GCP_PROJECT)
    ensure_table(bq_client)
    
    photo_zips = load_photo_zips()
    if not photo_zips:
        print("[!] No photo ZIP files found.")
        return
        
    total_loaded = 0
    for idx, zip_name in enumerate(photo_zips, 1):
        print(f"==========================================")
        print(f"Streaming Archive {idx} / {len(photo_zips)}: {zip_name}")
        print(f"==========================================")
        count = process_remote_zip(bq_client, zip_name)
        total_loaded += count
        print(f"[PROGRESS] Total cumulative photo sidecars loaded: {total_loaded}\n")

if __name__ == "__main__":
    main()
