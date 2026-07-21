import os
import sys
import json
import datetime
from pathlib import Path
from google.cloud import bigquery

sys.stdout.reconfigure(encoding="utf-8")

import fitz  # PyMuPDF
import pandas as pd

GCP_PROJECT = os.environ.get("GOOGLE_PROJECT_ID", "project-743aab84-f9a5-4ec7-954")
BQ_DATASET = "national_audits"
TABLE_NAME = "takeout_documents"
FULL_TABLE_ID = f"{GCP_PROJECT}.{BQ_DATASET}.{TABLE_NAME}"

WORKSPACE_DIR = r"C:\OsintNeoAi"
EXCLUDE_DIRS = {'.git', 'node_modules', 'venv', '__pycache__', '.gemini', '.vscode'}

def ensure_documents_table(bq_client):
    schema = [
        bigquery.SchemaField("file_path", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("file_name", "STRING"),
        bigquery.SchemaField("file_type", "STRING"),
        bigquery.SchemaField("extracted_text", "STRING"),
        bigquery.SchemaField("row_count", "INTEGER"),
        bigquery.SchemaField("col_count", "INTEGER"),
        bigquery.SchemaField("size_bytes", "INTEGER"),
        bigquery.SchemaField("ingest_timestamp", "TIMESTAMP")
    ]
    try:
        bq_client.get_table(FULL_TABLE_ID)
        print(f"[BQ] Table {FULL_TABLE_ID} verified.")
    except Exception:
        table_ref = bigquery.Table(FULL_TABLE_ID, schema=schema)
        table_ref.description = "Local and Cloud documents, spreadsheets, PDFs, and text ingested to BigQuery"
        bq_client.create_table(table_ref)
        print(f"[BQ] Created table {FULL_TABLE_ID}.")

def process_pdf(file_path):
    try:
        doc = fitz.open(file_path)
        text_parts = [page.get_text() for page in doc]
        return "\n".join(text_parts)[:500000]
    except Exception as e:
        return f"[PDF Error: {e}]"

def process_spreadsheet(file_path, file_type):
    try:
        if file_type == "csv":
            df = pd.read_csv(file_path, low_memory=False)
        else:
            df = pd.read_excel(file_path)
        rows, cols = df.shape
        summary_text = df.head(100).to_string(max_cols=20)
        return summary_text[:500000], rows, cols
    except Exception as e:
        return f"[Spreadsheet Error: {e}]", 0, 0

def process_text(file_path):
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()[:500000]
    except Exception as e:
        return f"[Text Error: {e}]"

def scan_local_documents():
    print("=" * 60)
    print("  OSINTNeoAi LOCAL DOCUMENT & SPREADSHEET INGESTION  ")
    print(f"  Target: {FULL_TABLE_ID}")
    print("=" * 60 + "\n")

    bq_client = bigquery.Client(project=GCP_PROJECT)
    ensure_documents_table(bq_client)

    supported_exts = {".pdf", ".csv", ".xlsx", ".xls", ".txt", ".json", ".md"}
    target_files = []

    for root, dirs, files in os.walk(WORKSPACE_DIR):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in supported_exts:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, WORKSPACE_DIR)
                size = os.path.getsize(full_path)
                target_files.append((full_path, rel_path, file, size, ext))

    print(f"[DOCS] Cataloged {len(target_files)} local documents/spreadsheets.")

    rows_to_insert = []
    scan_ts = datetime.datetime.now(datetime.UTC).isoformat()
    processed = 0

    for full_path, rel_path, file_name, size, ext in target_files:
        row_count, col_count = 0, 0
        file_type = ext.replace(".", "")

        if ext == ".pdf":
            extracted_text = process_pdf(full_path)
        elif ext in [".csv", ".xlsx", ".xls"]:
            extracted_text, row_count, col_count = process_spreadsheet(full_path, file_type)
        else:
            extracted_text = process_text(full_path)

        row = {
            "file_path": rel_path,
            "file_name": file_name,
            "file_type": file_type,
            "extracted_text": extracted_text,
            "row_count": row_count,
            "col_count": col_count,
            "size_bytes": size,
            "ingest_timestamp": scan_ts
        }
        rows_to_insert.append(row)
        processed += 1

        if len(rows_to_insert) >= 20:
            job_config = bigquery.LoadJobConfig(
                write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
                source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
            )
            job = bq_client.load_table_from_json(rows_to_insert, FULL_TABLE_ID, job_config=job_config)
            job.result()
            print(f"  ... [BQ LOAD] Ingested batch. Total documents loaded: {processed}")
            rows_to_insert = []

    if rows_to_insert:
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
        )
        job = bq_client.load_table_from_json(rows_to_insert, FULL_TABLE_ID, job_config=job_config)
        job.result()

    print(f"\n[✓] Local Document Ingestion Complete! Total loaded: {processed}")

if __name__ == "__main__":
    scan_local_documents()
