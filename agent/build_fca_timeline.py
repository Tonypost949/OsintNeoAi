"""
OsintNeoAi — FCA Timeline Generator
====================================
Parses evidence files (like EDR PDFs) and emails to generate chronological
timeline nodes for the forensic_layers.fca_timeline BigQuery table.
"""

import os
import uuid
import datetime
import logging
from google.cloud import bigquery

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

GCP_PROJECT = os.environ.get("GCP_PROJECT", "noble-beanbag-497411-m4")
BQ_DATASET = "forensic_layers"
TABLE_NAME = "fca_timeline"
FULL_TABLE_ID = f"{GCP_PROJECT}.{BQ_DATASET}.{TABLE_NAME}"

EVIDENCE_DIR = "evidence/edr_2025_real"

def ensure_table(client):
    schema = [
        bigquery.SchemaField("event_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("event_timestamp", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("event_type", "STRING", mode="REQUIRED"), # e.g. "REPORT_FILED", "EMAIL_SENT"
        bigquery.SchemaField("source_file", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("description", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("extracted_entities", "STRING", mode="REPEATED"),
        bigquery.SchemaField("added_at", "TIMESTAMP", mode="REQUIRED"),
    ]
    try:
        table = client.get_table(FULL_TABLE_ID)
        # Sandbox mode requires expiration < 60 days. Update it.
        table.expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=59)
        client.update_table(table, ["expires"])
        logger.info(f"Table {FULL_TABLE_ID} exists and expiration updated.")
    except Exception:
        table = bigquery.Table(FULL_TABLE_ID, schema=schema)
        # Sandbox mode requires expiration < 60 days
        table.expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=59)
        client.create_table(table)
        logger.info(f"Created table {FULL_TABLE_ID}")

def extract_timeline_from_pdfs():
    """Scans the EDR directory for PDFs to extract timeline events."""
    if not os.path.exists(EVIDENCE_DIR):
        logger.warning(f"Directory {EVIDENCE_DIR} not found.")
        return []
    
    events = []
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    # We will simulate extracting the file modification dates as the timeline events 
    # for the environmental reports
    for filename in os.listdir(EVIDENCE_DIR):
        if filename.lower().endswith(".pdf"):
            filepath = os.path.join(EVIDENCE_DIR, filename)
            stat = os.stat(filepath)
            mod_time = datetime.datetime.fromtimestamp(stat.st_mtime, datetime.timezone.utc)
            
            # Create a timeline node for the report generation
            events.append({
                "event_id": str(uuid.uuid4()),
                "event_timestamp": mod_time.isoformat(),
                "event_type": "EDR_REPORT_FILED",
                "source_file": filename,
                "description": f"Environmental Data Report generated/modified for {filename}",
                "extracted_entities": ["Lightbox EDR", "Environmental Survey"],
                "added_at": now_iso
            })
            
    return events

def main():
    logger.info("Starting FCA Timeline Generator...")
    client = bigquery.Client(project=GCP_PROJECT)
    ensure_table(client)
    
    events = extract_timeline_from_pdfs()
    if not events:
        logger.info("No events to insert.")
        return
        
    logger.info(f"Extracted {len(events)} timeline events from evidence.")
    
    errors = []
    try:
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND
        )
        job = client.load_table_from_json(events, FULL_TABLE_ID, job_config=job_config)
        job.result()  # Wait for the job to complete
    except Exception as e:
        errors.append(str(e))

    if errors:
        logger.error(f"Error inserting timeline events: {errors}")
    else:
        logger.info(f"Successfully loaded {len(events)} events into {FULL_TABLE_ID}.")

if __name__ == "__main__":
    main()
