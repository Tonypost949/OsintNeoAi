"""
load_files_to_bq.py — Load OC procurement file index into BigQuery
Loads oc_procurement_files_full.json → ppp_rico.oc_procurement_files
"""
import json, csv
from pathlib import Path
from datetime import datetime
from google.cloud import bigquery

WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")
IN_JSON = WORK_DIR / "oc_procurement_files_full.json"
PROJECT = "noble-beanbag-497411-m4"
DATASET = "ppp_rico"
TABLE = "oc_procurement_files"

client = bigquery.Client(project=PROJECT)

schema = [
    bigquery.SchemaField("project_numeric_id", "STRING"),
    bigquery.SchemaField("project_financial_id", "STRING"),
    bigquery.SchemaField("project_title", "STRING"),
    bigquery.SchemaField("project_url", "STRING"),
    bigquery.SchemaField("file_name", "STRING"),
    bigquery.SchemaField("display_name", "STRING"),
    bigquery.SchemaField("s3_bucket", "STRING"),
    bigquery.SchemaField("s3_path", "STRING"),
    bigquery.SchemaField("download_url", "STRING"),
    bigquery.SchemaField("scraped_at", "TIMESTAMP"),
    bigquery.SchemaField("loaded_at", "TIMESTAMP"),
]

table_ref = f"{PROJECT}.{DATASET}.{TABLE}"

if not IN_JSON.exists():
    print(f"ERROR: {IN_JSON} not found.")
    exit(1)

with open(IN_JSON, "r", encoding="utf-8") as f:
    rows = json.load(f)

print(f"Loaded {len(rows)} file rows from {IN_JSON}")

if not rows:
    print("No rows to load.")
    exit(0)

now = datetime.now().isoformat()

ndjson_path = WORK_DIR / "oc_procurement_files_load.ndjson"
with open(ndjson_path, "w", encoding="utf-8") as f:
    for r in rows:
        row = {
            "project_numeric_id": r.get("project_numeric_id", ""),
            "project_financial_id": r.get("project_financial_id", ""),
            "project_title": r.get("project_title", ""),
            "project_url": r.get("project_url", ""),
            "file_name": r.get("file_name", ""),
            "display_name": r.get("display_name", ""),
            "s3_bucket": r.get("s3_bucket", ""),
            "s3_path": r.get("s3_path", ""),
            "download_url": r.get("download_url", ""),
            "scraped_at": r.get("scraped_at", now),
            "loaded_at": now,
        }
        f.write(json.dumps(row) + "\n")

print(f"NDJSON written: {ndjson_path}")

try:
    client.delete_table(table_ref, not_found_ok=True)
    print(f"Dropped existing table {table_ref}")

    table = bigquery.Table(table_ref, schema=schema)
    table = client.create_table(table)
    print(f"Created table {table_ref}")

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        autodetect=False,
        schema=schema,
    )

    with open(ndjson_path, "rb") as source_file:
        load_job = client.load_table_from_file(source_file, table_ref, job_config=job_config)

    load_job.result()

    dest_table = client.get_table(table_ref)
    print(f"Loaded {dest_table.num_rows} rows into {table_ref}")

    # Preview
    preview = client.query(
        f"SELECT project_numeric_id, file_name, display_name, s3_bucket FROM `{table_ref}` LIMIT 10"
    ).to_dataframe()
    print("\nPreview:")
    print(preview.to_string(max_colwidth=60))

except Exception as e:
    print(f"BigQuery error: {e}")
    import traceback
    traceback.print_exc()
