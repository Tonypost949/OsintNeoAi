import urllib.request
import urllib.error
import ssl
import pandas as pd
from google.cloud import bigquery
import os
import re

def download_and_ingest():
    file_url = "https://www.sco.ca.gov/Files-UPD/estates_of_deceased_persons_file.xlsx"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    dest_path = "estates_deceased_persons.xlsx"
    
    print("Downloading raw unclaimed database file...")
    try:
        req = urllib.request.Request(file_url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
            with open(dest_path, "wb") as f:
                f.write(response.read())
        print("Successfully downloaded dataset file.")
        
        print("Reading Excel sheet (skipping header lines)...")
        df = pd.read_excel(dest_path, skiprows=3)
        print(f"Rows: {len(df)} | Columns count: {len(df.columns)}")
        
        # Clean column names strictly according to BigQuery schema guidelines:
        # Must contain only letters, numbers, and underscores, start with a letter or underscore, 
        # and be at most 300 characters long.
        cleaned_cols = []
        for i, col in enumerate(df.columns):
            c_str = str(col).strip()
            # Remove invalid characters
            c_clean = re.sub(r'[^a-zA-Z0-9_]', '_', c_str)
            # Ensure it starts with a letter or underscore
            if not c_clean or not re.match(r'^[a-zA-Z_]', c_clean):
                c_clean = f"col_{c_clean}" if c_clean else f"col_{i}"
            
            cleaned_cols.append(c_clean.lower())
        
        df.columns = cleaned_cols
        print(f"Sanitized columns for BigQuery: {df.columns}")
        
        # Convert all columns to strings
        for col in df.columns:
            df[col] = df[col].astype(str).replace('nan', None)
            
        # Ingest to BigQuery
        bq = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")
        table_id = "project-743aab84-f9a5-4ec7-954.unclaimed_property.ca_unclaimed_raw"
        
        print(f"Loading {len(df)} records into BigQuery table {table_id}...")
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
        )
        
        job = bq.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()
        print("Successfully loaded rows into BigQuery.")
        
        # Query results
        print("Searching database for Mercy House & Larry Haynes...")
        conditions = []
        for col in df.columns:
            conditions.append(f"UPPER({col}) LIKE '%MERCY%'")
            conditions.append(f"UPPER({col}) LIKE '%HAYNES%'")
        
        where_clause = " OR ".join(conditions)
        q = f"SELECT * FROM `{table_id}` WHERE {where_clause} LIMIT 20"
        
        results = bq.query(q).to_dataframe()
        if len(results) > 0:
            print("Found matches:")
            print(results.to_string())
            
            # Send email notification
            from send_email import send_evidence_alert
            body = "Found matching unclaimed property records in the California database:\n\n" + results.to_string()
            send_evidence_alert("ALERT: CA Unclaimed Property Matches Found", body)
        else:
            print("No records found in this dataset.")
            
    except Exception as e:
        print(f"Error: {e}")

download_and_ingest()
