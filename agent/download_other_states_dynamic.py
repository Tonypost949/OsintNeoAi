import urllib.request
import json
import ssl
import pandas as pd
from google.cloud import bigquery
import re

def download_dynamic_state_datasets():
    # We query the Socrata catalog API used by state data portals to dynamically find the correct CSV export download URLs
    portals = {
        "texas": "https://data.texas.gov/api/views/pq23-y2sz.json", # Texas Unclaimed Metadata
        "new_york": "https://data.ny.gov/api/views/pq92-u5sz.json"  # NY Unclaimed Metadata
    }
    
    bq = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    headers = {"User-Agent": "Mozilla/5.0"}
    
    for state, meta_url in portals.items():
        print(f"\n=== PROCESSING STATE: {state.upper()} ===")
        try:
            # Query Socrata API to get dataset information
            req = urllib.request.Request(meta_url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
                meta_data = json.loads(response.read().decode('utf-8'))
                # Extract CSV download URL
                # If the dataset ID is pq23-y2sz, the CSV link is /api/views/pq23-y2sz/rows.csv?accessType=DOWNLOAD
                dataset_id = meta_data.get("id")
                domain = re.search(r'https://[^/]+', meta_url).group(0)
                csv_url = f"{domain}/api/views/{dataset_id}/rows.csv?accessType=DOWNLOAD"
                print(f"Dynamic CSV URL: {csv_url}")
                
                dest_csv = f"{state}_unclaimed_dynamic.csv"
                print("Downloading dataset...")
                csv_req = urllib.request.Request(csv_url, headers=headers)
                with urllib.request.urlopen(csv_req, context=ctx, timeout=45) as csv_resp:
                    with open(dest_csv, "wb") as f:
                        f.write(csv_resp.read())
                print(f"Successfully downloaded {state} CSV.")
                
                # Ingest to BigQuery
                df = pd.read_csv(dest_csv, nrows=10000)
                cleaned_cols = []
                for i, col in enumerate(df.columns):
                    c_str = str(col).strip()
                    c_clean = re.sub(r'[^a-zA-Z0-9_]', '_', c_str)
                    if not c_clean or not re.match(r'^[a-zA-Z_]', c_clean):
                        c_clean = f"col_{i}"
                    cleaned_cols.append(c_clean.lower())
                df.columns = cleaned_cols
                
                for col in df.columns:
                    df[col] = df[col].astype(str).replace('nan', None)
                    
                table_id = f"project-743aab84-f9a5-4ec7-954.unclaimed_property.{state}_unclaimed_raw"
                print(f"Loading {len(df)} rows into table {table_id}...")
                job_config = bigquery.LoadJobConfig(
                    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
                )
                job = bq.load_table_from_dataframe(df, table_id, job_config=job_config)
                job.result()
                print(f"Successfully loaded {state} data into BigQuery.")
                
        except Exception as e:
            print(f"Error processing {state}: {e}")

if __name__ == "__main__":
    download_dynamic_state_datasets()
