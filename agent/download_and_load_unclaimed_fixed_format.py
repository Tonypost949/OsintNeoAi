import urllib.request
import urllib.error
import ssl
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
    
    print("Downloading raw unclaimed database file...")
    try:
        req = urllib.request.Request(file_url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
            with open(dest_path, "wb") as f:
                f.write(response.read())
        print("Successfully downloaded dataset file.")
        
        print("Reading Excel sheet (skipping header lines)...")
        # The file has title rows. Let's skip the first 3 rows to align headers properly.
        df = pd.read_excel(dest_path, skiprows=3)
        print(f"Rows: {len(df)} | Columns: {list(df.columns)}")
        
        # Clean column names
        df.columns = [str(c).strip().replace(' ', '_').replace('/', '_').replace('-', '_').lower() for c in df.columns]
        
        # Remove empty columns or columns named 'unnamed:...'
        df = df[[c for c in df.columns if not c.startswith('unnamed')]]
        
        # Convert all columns to strings to prevent schema mismatches
        for col in df.columns:
            df[col] = df[col].astype(str).replace('nan', None)
            
        print(f"Cleaned columns for BigQuery: {list(df.columns)}")
        
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
        else:
            print("No records found in this dataset.")
            
    except Exception as e:
        print(f"Error: {e}")

download_and_ingest()
