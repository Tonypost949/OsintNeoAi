import urllib.request
import urllib.error
import ssl
import re
import pandas as pd
from google.cloud import bigquery
import os

def download_and_ingest():
    file_url = "https://www.sco.ca.gov/Files-UPD/estates_of_deceased_persons_file.xlsx"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    dest_path = "estates_deceased_persons.xlsx"
    
    if not os.path.exists(dest_path):
        print("Downloading raw unclaimed database file...")
        try:
            req = urllib.request.Request(file_url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=60) as response:
                with open(dest_path, "wb") as f:
                    f.write(response.read())
            print("Successfully downloaded dataset file.")
        except Exception as e:
            print(f"Download error: {e}")
            return
    else:
        print("Using cached estates_deceased_persons.xlsx (already downloaded).")
    
    print("Reading Excel sheet (skipping header lines)...")
    df = pd.read_excel(dest_path, skiprows=3)
    print(f"Rows: {len(df)} | Raw columns count: {len(df.columns)}")
    
    # Assign proper column names based on the SCO Estates of Deceased Persons schema
    proper_names = [
        "case_id", "estate_number", "decedent_or_heir_name", "role",
        "date_field_1", "date_field_2", "escheat_date",
        "escheat_status", "report_date", "received_date",
        "petition_number", "amount_1", "amount_2", "county"
    ]
    
    if len(df.columns) <= len(proper_names):
        df.columns = proper_names[:len(df.columns)]
    else:
        # More columns than expected - name extras generically
        extra = [f"extra_col_{i}" for i in range(len(df.columns) - len(proper_names))]
        df.columns = proper_names + extra
    
    print(f"Assigned columns: {list(df.columns)}")
    
    # Convert all columns to strings for safe BQ ingestion
    for col in df.columns:
        df[col] = df[col].astype(str).replace('nan', None).replace('NaT', None)
        
    # Ingest to BigQuery
    bq = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")
    table_id = "project-743aab84-f9a5-4ec7-954.unclaimed_property.ca_unclaimed_raw"
    
    print(f"Loading {len(df)} records into BigQuery table {table_id}...")
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
    )
    
    job = bq.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()
    print(f"Successfully loaded {len(df)} rows into BigQuery.")
    
    # Query for targets
    print("Searching database for Mercy House & Larry Haynes...")
    search_terms = ['MERCY', 'HAYNES', 'LARRY']
    text_cols = ['decedent_or_heir_name', 'escheat_status', 'county']
    
    conditions = []
    for col in text_cols:
        for term in search_terms:
            conditions.append(f"UPPER({col}) LIKE '%{term}%'")
    
    where_clause = " OR ".join(conditions)
    q = f"SELECT * FROM `{table_id}` WHERE {where_clause} LIMIT 50"
    
    results = bq.query(q).to_dataframe()
    if len(results) > 0:
        print(f"Found {len(results)} matching records:")
        print(results.to_string())
        
        # Send email alert (no unicode emojis)
        try:
            from send_email import send_evidence_alert
            body = f"Found {len(results)} matching unclaimed property records in the California Estates of Deceased Persons database:\n\n" + results.to_string()
            send_evidence_alert("ALERT: CA Unclaimed Property Matches Found", body)
            print("Email notification sent.")
        except Exception as e:
            print(f"Email notification failed: {e}")
    else:
        print("No records found matching search terms.")

download_and_ingest()
