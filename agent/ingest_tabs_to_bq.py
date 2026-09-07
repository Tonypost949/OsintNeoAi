import os
import re
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

def ensure_table(client):
    try:
        dataset = client.get_dataset(f"{GCP_PROJECT}.{BQ_DATASET}")
        dataset.default_table_expiration_ms = 59 * 24 * 60 * 60 * 1000 # 59 days
        dataset.default_partition_expiration_ms = 59 * 24 * 60 * 60 * 1000 # 59 days
        client.update_dataset(dataset, ["default_table_expiration_ms", "default_partition_expiration_ms"])
    except Exception as e:
        logger.warning(f"Could not update dataset expiration: {e}")
    try:
        table = client.get_table(FULL_TABLE_ID)
        table.expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=59)
        client.update_table(table, ["expires"])
    except Exception:
        pass

def parse_evidence_file(filepath):
    events = []
    if not os.path.exists(filepath):
        logger.error(f"File not found: {filepath}")
        return events
        
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Split by the numbering pattern "1) ", "2) ", etc.
    blocks = re.split(r'\n\d+\)\s+', "\n" + content)
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    for block in blocks:
        block = block.strip()
        if not block:
            continue
            
        lines = block.split("\n")
        title = lines[0].strip()
        url = ""
        
        for line in lines:
            if line.startswith("URL:"):
                url = line.replace("URL:", "").strip()
                break
                
        if title and url:
            events.append({
                "event_id": str(uuid.uuid4()),
                "event_timestamp": now_iso,
                "event_type": "OSINT_TAB_EVIDENCE",
                "source_file": "hb_cameron_lane_evidence.txt",
                "description": f"Target: {title} | URL: {url}",
                "extracted_entities": ["Huntington Beach", "Cameron Lane", "Hexavalent Chromium"],
                "added_at": now_iso
            })
            
    return events

def main():
    client = bigquery.Client(project=GCP_PROJECT)
    ensure_table(client)
    filepath = "data/hb_cameron_lane_evidence.txt"
    
    events = parse_evidence_file(filepath)
    if not events:
        logger.info("No events parsed.")
        return
        
    logger.info(f"Parsed {len(events)} OSINT targets. Loading to BigQuery...")
    
    try:
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND
        )
        job = client.load_table_from_json(events, FULL_TABLE_ID, job_config=job_config)
        job.result()
        logger.info(f"Successfully loaded {len(events)} OSINT evidence nodes into {FULL_TABLE_ID}.")
    except Exception as e:
        logger.error(f"Failed to load to BigQuery: {e}")

if __name__ == "__main__":
    main()
