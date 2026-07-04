import urllib.request
import urllib.error
import ssl
import pandas as pd
from google.cloud import bigquery
import os

# We will download public raw unclaimed property database exports from other major states.
# Texas, Florida, and New York publish their unclaimed datasets on state open data portals.

def download_state_datasets():
    bq = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    headers = {"User-Agent": "Mozilla/5.0"}
    
    # State dataset URLs
    states = {
        "texas": "https://data.texas.gov/api/views/pq23-y2sz/rows.csv?accessType=DOWNLOAD", # Texas unclaimed property data
        "new_york": "https://data.ny.gov/api/views/pq92-u5sz/rows.csv?accessType=DOWNLOAD" # NY unclaimed property index
    }
    
    for state, url in states.items():
        print(f"\n=== DOWNLOADING RAW DATASET FOR STATE: {state.upper()} ===")
        dest_csv = f"{state}_unclaimed.csv"
        
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=60) as response:
                with open(dest_csv, "wb") as f:
                    f.write(response.read())
            print(f"Successfully downloaded {state} CSV dataset.")
            
            # Load and clean column headers
            df = pd.read_csv(dest_csv, nrows=50000) # Load first 50k rows to prevent memory overload
            print(f"Loaded {len(df)} rows. Cleaning headers...")
            
            cleaned_cols = []
            for i, col in enumerate(df.columns):
                c_str = str(col).strip()
                if not c_str or c_str.startswith('Unnamed'):
                    cleaned_cols.append(f"col_{i}")
                else:
                    cleaned_cols.append(c_str.replace(' ', '_').replace('/', '_').replace('-', '_').lower())
            df.columns = cleaned_cols
            
            # Convert all columns to strings
            for col in df.columns:
                df[col] = df[col].astype(str).replace('nan', None)
                
            table_id = f"project-743aab84-f9a5-4ec7-954.unclaimed_property.{state}_unclaimed_raw"
            print(f"Loading {len(df)} rows into table {table_id}...")
            
            job_config = bigquery.LoadJobConfig(
                write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
            )
            
            job = bq.load_table_from_dataframe(df, table_id, job_config=job_config)
            job.result()
            print(f"✅ Successfully loaded {state} data into BigQuery.")
            
        except Exception as e:
            print(f"Error processing {state} dataset: {e}")

if __name__ == "__main__":
    download_state_datasets()
