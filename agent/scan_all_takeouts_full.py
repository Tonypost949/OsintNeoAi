import os
import sys
import json
import subprocess
import io
import zipfile
import datetime
from google.cloud import bigquery

sys.stdout.reconfigure(encoding="utf-8")

GCP_PROJECT = "project-743aab84-f9a5-4ec7-954"
DATASET_ID = "national_audits"
TABLE_ID = "google_photos_index"
FULL_TABLE_ID = f"{GCP_PROJECT}.{DATASET_ID}.{TABLE_ID}"
REMOTE_DIR = "gdrive:Sharedall/takeouts all 22226"

class RcloneFile(io.RawIOBase):
    def __init__(self, rclone_path):
        self.rclone_path = rclone_path
        self.offset = 0
        cmd = ["rclone", "size", rclone_path, "--json"]
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
        length = len(b)
        if self.offset >= self.size:
            return 0
        count = min(length, self.size - self.offset)
        cmd = ["rclone", "cat", self.rclone_path, "--offset", str(self.offset), "--count", str(count)]
        res = subprocess.run(cmd, capture_output=True)
        data = res.stdout
        b[:len(data)] = data
        self.offset += len(data)
        return len(data)

def ensure_bq_schema(client):
    schema = [
        bigquery.SchemaField("photo_id", "STRING"),
        bigquery.SchemaField("filename", "STRING"),
        bigquery.SchemaField("mime_type", "STRING"),
        bigquery.SchemaField("creation_time", "TIMESTAMP"),
        bigquery.SchemaField("camera_make", "STRING"),
        bigquery.SchemaField("camera_model", "STRING"),
        bigquery.SchemaField("focal_length", "FLOAT"),
        bigquery.SchemaField("aperture", "FLOAT"),
        bigquery.SchemaField("iso_equivalent", "INTEGER"),
        bigquery.SchemaField("latitude", "FLOAT"),
        bigquery.SchemaField("longitude", "FLOAT"),
        bigquery.SchemaField("description", "STRING"),
        bigquery.SchemaField("source_zip", "STRING"),
        bigquery.SchemaField("file_path", "STRING"),
        bigquery.SchemaField("ingest_timestamp", "TIMESTAMP"),
    ]
    try:
        table = client.get_table(FULL_TABLE_ID)
        existing_cols = {f.name for f in table.schema}
        new_fields = list(table.schema)
        added = False
        for f in schema:
            if f.name not in existing_cols:
                new_fields.append(f)
                added = True
        if added:
            table.schema = new_fields
            client.update_table(table, ["schema"])
            print(f"[BQ] Updated schema for {FULL_TABLE_ID}")
    except Exception as e:
        print(f"[BQ] Creating table {FULL_TABLE_ID}...")
        table_obj = bigquery.Table(FULL_TABLE_ID, schema=schema)
        client.create_table(table_obj)

def parse_photo_metadata(json_content, zip_name, file_path):
    try:
        data = json.loads(json_content.decode('utf-8', errors='ignore'))
        if not isinstance(data, dict):
            return None

        title = data.get("title") or os.path.basename(file_path).replace(".json", "")
        desc = data.get("description", "")
        
        # Creation time
        creation_time_str = None
        taken_time = data.get("photoTakenTime", {})
        if isinstance(taken_time, dict):
            ts = taken_time.get("timestamp")
            if ts:
                try:
                    dt = datetime.datetime.utcfromtimestamp(float(ts))
                    creation_time_str = dt.isoformat() + "Z"
                except Exception:
                    pass
            if not creation_time_str and taken_time.get("formatted"):
                creation_time_str = taken_time.get("formatted")

        # Geo coordinates
        lat = None
        lon = None
        geo = data.get("geoData", {})
        if isinstance(geo, dict):
            lat = geo.get("latitude")
            lon = geo.get("longitude")
            if lat == 0.0 and lon == 0.0:
                geo_exif = data.get("geoDataExif", {})
                if isinstance(geo_exif, dict):
                    lat = geo_exif.get("latitude") or None
                    lon = geo_exif.get("longitude") or None
            if lat == 0.0 and lon == 0.0:
                lat = None
                lon = None

        now_iso = datetime.datetime.utcnow().isoformat() + "Z"

        return {
            "photo_id": f"{zip_name}:{file_path}",
            "filename": title,
            "mime_type": "image/jpeg" if title.lower().endswith(('.jpg', '.jpeg')) else "image/png",
            "creation_time": creation_time_str,
            "camera_make": None,
            "camera_model": None,
            "focal_length": None,
            "aperture": None,
            "iso_equivalent": None,
            "latitude": float(lat) if lat is not None else None,
            "longitude": float(lon) if lon is not None else None,
            "description": desc[:1000] if desc else None,
            "source_zip": zip_name,
            "file_path": file_path,
            "ingest_timestamp": now_iso
        }
    except Exception:
        return None

def process_remote_zip(zip_name, bq_client):
    full_path = f"{REMOTE_DIR}/{zip_name}"
    print(f"\n--- Scanning remote ZIP: {zip_name} ---")
    rows = []
    try:
        rfile = RcloneFile(full_path)
        with zipfile.ZipFile(rfile) as z:
            namelist = z.namelist()
            json_meta_files = [n for n in namelist if "Takeout/Google Photos/" in n and n.endswith(".json")]
            print(f"Found {len(json_meta_files)} photo metadata files in {zip_name}.")
            
            for idx, json_path in enumerate(json_meta_files):
                try:
                    content = z.read(json_path)
                    row = parse_photo_metadata(content, zip_name, json_path)
                    if row:
                        rows.append(row)
                except Exception as e:
                    pass

                if len(rows) >= 500:
                    flush_to_bq(rows, bq_client)
                    rows = []

        if rows:
            flush_to_bq(rows, bq_client)
            rows = []
    except Exception as e:
        print(f"[!] Error processing {zip_name}: {e}")

def flush_to_bq(rows, bq_client):
    if not rows:
        return
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
    )
    job = bq_client.load_table_from_json(rows, FULL_TABLE_ID, job_config=job_config)
    job.result()
    print(f"  [BQ] Inserted batch of {len(rows)} rows into {FULL_TABLE_ID}.")

def main():
    bq_client = bigquery.Client(project=GCP_PROJECT)
    ensure_bq_schema(bq_client)

    print(f"[SCAN] Fetching ZIP list from {REMOTE_DIR}...")
    cmd = ["rclone", "lsf", REMOTE_DIR, "--include", "*.zip"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    zip_files = [f.strip() for f in res.stdout.splitlines() if f.strip().endswith(".zip")]
    print(f"[SCAN] Total ZIP files found: {len(zip_files)}")

    for idx, zip_name in enumerate(zip_files):
        print(f"\n[{idx+1}/{len(zip_files)}] Processing {zip_name}...")
        process_remote_zip(zip_name, bq_client)

    print("\n[✓] All Takeout ZIP files scanned and loaded into BigQuery successfully!")

if __name__ == "__main__":
    main()
