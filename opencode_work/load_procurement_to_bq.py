"""
load_procurement_to_bq.py — Load OC procurement projects into BigQuery
After scrape_oc_procurement.py runs, this loads the JSON into ppp_rico.oc_procurement
Also runs geocoding on addresses found in project descriptions
"""
import json, sys
from pathlib import Path
from datetime import datetime
from google.cloud import bigquery

WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")
IN_JSON = WORK_DIR / "oc_procurement_projects.json"
PROJECT = "noble-beanbag-497411-m4"
DATASET = "ppp_rico"
TABLE = "oc_procurement"

client = bigquery.Client(project=PROJECT)

# Create table schema
schema = [
    bigquery.SchemaField("title", "STRING"),
    bigquery.SchemaField("url", "STRING"),
    bigquery.SchemaField("department", "STRING"),
    bigquery.SchemaField("status", "STRING"),
    bigquery.SchemaField("category", "STRING"),
    bigquery.SchemaField("deadline", "STRING"),
    bigquery.SchemaField("published", "STRING"),
    bigquery.SchemaField("description", "STRING"),
    bigquery.SchemaField("amount_est", "FLOAT64"),
    bigquery.SchemaField("vendor_name", "STRING"),
    bigquery.SchemaField("page", "INTEGER"),
    bigquery.SchemaField("scraped_at", "TIMESTAMP"),
    bigquery.SchemaField("loaded_at", "TIMESTAMP"),
]

table_ref = f"{PROJECT}.{DATASET}.{TABLE}"

# Load JSON
if not IN_JSON.exists():
    print(f"ERROR: {IN_JSON} not found. Run scrape_oc_procurement.py first.")
    sys.exit(1)

with open(IN_JSON, "r", encoding="utf-8") as f:
    projects = json.load(f)

print(f"Loaded {len(projects)} projects from {IN_JSON}")

if not projects:
    print("No projects to load. Exiting.")
    sys.exit(0)

# Enrich: extract dollar amounts and vendor names from descriptions
import re

for p in projects:
    desc = p.get("description", "") + " " + p.get("title", "")
    # Dollar amounts
    amounts = re.findall(r'\$[\d,]+(?:\.\d+)?|\d[\d,]*\s*(?:million|billion)', desc, re.IGNORECASE)
    if amounts:
        try:
            raw = amounts[0].replace("$", "").replace(",", "").strip()
            if "million" in raw.lower():
                p["amount_est"] = float(raw.split()[0].replace("$","").replace(",","")) * 1e6
            elif "billion" in raw.lower():
                p["amount_est"] = float(raw.split()[0].replace("$","").replace(",","")) * 1e9
            else:
                p["amount_est"] = float(raw)
        except:
            p["amount_est"] = None
    else:
        p["amount_est"] = None
    
    # Vendor/contractor names (words after "awarded to", "vendor:", "contractor:", etc.)
    vendor_match = re.search(r'(?:awarded to|vendor|contractor|awardee)[:\s]+([A-Z][A-Za-z\s&.,]+?)(?:\.|,|$|\n)', desc, re.IGNORECASE)
    p["vendor_name"] = vendor_match.group(1).strip() if vendor_match else None
    
    p["loaded_at"] = datetime.now().isoformat()
    # Ensure scraped_at is a string
    if not p.get("scraped_at"):
        p["scraped_at"] = datetime.now().isoformat()

# Create temp NDJSON for BQ load
ndjson_path = WORK_DIR / "oc_procurement_load.ndjson"
with open(ndjson_path, "w", encoding="utf-8") as f:
    for p in projects:
        row = {
            "title": p.get("title", ""),
            "url": p.get("url", ""),
            "department": p.get("department", ""),
            "status": p.get("status", ""),
            "category": p.get("category", ""),
            "deadline": p.get("deadline", ""),
            "published": p.get("published", ""),
            "description": p.get("description", ""),
            "amount_est": p.get("amount_est"),
            "vendor_name": p.get("vendor_name"),
            "page": p.get("page", 0),
            "scraped_at": p.get("scraped_at", datetime.now().isoformat()),
            "loaded_at": p.get("loaded_at", datetime.now().isoformat()),
        }
        f.write(json.dumps(row) + "\n")

print(f"NDJSON written: {ndjson_path}")

# Create or replace table and load
try:
    # Drop if exists
    client.delete_table(table_ref, not_found_ok=True)
    print(f"Dropped existing table {table_ref}")
    
    # Create table
    table = bigquery.Table(table_ref, schema=schema)
    table = client.create_table(table)
    print(f"Created table {table_ref}")
    
    # Load data
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
    preview = client.query(f"SELECT title, department, status, amount_est, vendor_name FROM `{table_ref}` LIMIT 10").to_dataframe()
    print("\nPreview:")
    print(preview.to_string(max_colwidth=60))
    
except Exception as e:
    print(f"BigQuery error: {e}")
    import traceback
    traceback.print_exc()