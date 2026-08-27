"""
ingest_photos_evidence_to_bigquery.py — Ingests extracted Google Photos evidence & OCR records into BigQuery target dataset.
"""
import os
import json
import datetime
from google.cloud import bigquery

PROJECT = "noble-beanbag-497411-m4"
DATASET = "national_audits"
TABLE_NAME = "google_photos_evidence_ocr"
INPUT_PATH = "data/google_photos_evidence_ocr.json"

def main():
    if not os.path.exists(INPUT_PATH):
        print(f"[-] Input file not found: {INPUT_PATH}")
        return

    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        records = json.load(f)

    print(f"[*] Loaded {len(records)} extracted evidence records from {INPUT_PATH}")
    client = bigquery.Client(project=PROJECT)
    table_id = f"{PROJECT}.{DATASET}.{TABLE_NAME}"

    # Define table schema
    schema = [
        bigquery.SchemaField("item_index", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("photo_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("image_url", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("width", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("height", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("media_timestamp", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("analysis_transcript", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("ingest_timestamp", "TIMESTAMP", mode="REQUIRED"),
    ]

    try:
        table = client.get_table(table_id)
        print(f"[+] Found existing table {table_id}")
    except Exception:
        table = bigquery.Table(table_id, schema=schema)
        table = client.create_table(table)
        print(f"[+] Created new BigQuery table: {table_id}")

    rows_to_insert = []
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    for r in records:
        ts = r.get("timestamp")
        dt_str = datetime.datetime.fromtimestamp(ts / 1000.0, datetime.timezone.utc).isoformat() if ts else None

        rows_to_insert.append({
            "item_index": r.get("index"),
            "photo_id": r.get("id"),
            "image_url": r.get("image_url"),
            "width": r.get("width"),
            "height": r.get("height"),
            "media_timestamp": dt_str,
            "analysis_transcript": r.get("analysis"),
            "ingest_timestamp": now_iso
        })

    errors = client.insert_rows_json(table_id, rows_to_insert)
    if errors:
        print(f"[-] BigQuery insert encountered errors: {errors}")
    else:
        print(f"[+] Successfully streamed {len(rows_to_insert)} evidence records to {table_id}")

if __name__ == "__main__":
    main()
