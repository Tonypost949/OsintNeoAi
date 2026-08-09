import urllib.request
import urllib.error
import ssl
import pandas as pd
from google.cloud import bigquery
import os

def download_and_ingest():
    # Direct link to the Excel file from SCO website
    # First, let's find the exact link. Often, the link is structured like:
    # https://www.sco.ca.gov/Files-UPD/estates_deceased_persons.xlsx or similar.
    # Let's request the page and extract the link dynamically.
    
    url = "https://www.sco.ca.gov/upd_estates_investigator.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    file_url = None
    print("Fetching State Controller investigator page...")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            html = response.read().decode('utf-8')
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            for a in soup.find_all('a'):
                href = a.get('href', '')
                if 'estates' in href.lower() and (href.endswith('.xlsx') or href.endswith('.xls') or href.endswith('.zip')):
                    if href.startswith('http'):
                        file_url = href
                    else:
                        file_url = "https://www.sco.ca.gov/" + href.lstrip('/')
                    break
    except Exception as e:
        print(f"Error reading investigator page: {e}")

    # Fallback to standard known URL if not found dynamically
    if not file_url:
        file_url = "https://www.sco.ca.gov/Files-UPD/estates_deceased_persons.xlsx"
        
    print(f"Target dataset URL: {file_url}")
    dest_path = "estates_deceased_persons.xlsx"
    
    print("Downloading raw unclaimed database file...")
    try:
        req = urllib.request.Request(file_url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
            with open(dest_path, "wb") as f:
                f.write(response.read())
        print(f"✅ Successfully downloaded dataset to {dest_path}")
        
        # Load and verify Excel sheet
        print("Reading Excel sheet...")
        df = pd.read_excel(dest_path)
        print(f"Rows: {len(df)} | Columns: {list(df.columns)}")
        
        # Clean column names for BigQuery compatibility (no spaces, lower case)
        df.columns = [c.strip().replace(' ', '_').replace('/', '_').replace('-', '_').lower() for c in df.columns]
        print(f"Cleaned columns: {df.columns}")
        
        # Ingest to BigQuery
        bq = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")
        table_id = "project-743aab84-f9a5-4ec7-954.unclaimed_property.ca_unclaimed_raw"
        
        print(f"Loading {len(df)} records into BigQuery table {table_id}...")
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
        )
        
        job = bq.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result() # Wait for upload to complete
        print(f"✅ Successfully loaded {len(df)} rows into {table_id}")
        
        # Query the newly loaded table for Mercy House / Larry Haynes
        print("\n=== RUNNING VERIFICATION QUERY ON NEW DATA ===")
        # Search all string columns
        str_cols = [c for c in df.columns if df[c].dtype == 'object']
        conditions = []
        for col in str_cols:
            conditions.append(f"UPPER({col}) LIKE '%MERCY%'")
            conditions.append(f"UPPER({col}) LIKE '%HAYNES%'")
        
        where_clause = " OR ".join(conditions)
        q = f"SELECT * FROM `{table_id}` WHERE {where_clause} LIMIT 20"
        
        results = bq.query(q).to_dataframe()
        if len(results) > 0:
            print(f"✅ Found matches in ca_unclaimed_raw:")
            print(results.to_string())
        else:
            print("No matching unclaimed property records found in the official Estates of Deceased Persons database.")
            
    except Exception as e:
        print(f"Error during download or ingestion: {e}")

download_and_ingest()
