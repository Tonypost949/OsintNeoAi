import pandas as pd
from google.cloud import bigquery
import os

def ingest_file(client, file_path, table_id):
    print(f"Reading {file_path}...")
    # Read the text file using pandas
    df = pd.read_csv(file_path, low_memory=False)
    
    # Clean column names (replace any non-alphanumeric chars with underscores)
    import re
    df.columns = [re.sub(r'[^a-zA-Z0-9_]', '_', c).strip('_') for c in df.columns]
    # Collapse multiple underscores
    df.columns = [re.sub(r'_+', '_', c) for c in df.columns]
    
    # Convert all columns to strings to avoid BQ type detection mismatches
    df = df.astype(str)
    
    # Replace 'NULL', 'nan', 'None' with actual None (for Nullable fields)
    df = df.replace({'NULL': None, 'nan': None, 'None': None})

    print(f"Uploading {len(df)} rows to {table_id}...")
    
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",
    )
    
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result() # Wait for job to complete
    print(f"Ingested {table_id} successfully.")

def main():
    client = bigquery.Client(project='project-743aab84-f9a5-4ec7-954')
    
    base_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\extracted\APT2024filesfull (Unzipped Files)\TXT"
    
    files_to_ingest = {
        "beeline-crm.txt": "project-743aab84-f9a5-4ec7-954.ppp_rico.beeline_crm",
        "beeline-lbs.txt": "project-743aab84-f9a5-4ec7-954.ppp_rico.beeline_lbs",
        "beeline-cdr.txt": "project-743aab84-f9a5-4ec7-954.ppp_rico.beeline_cdr",
        "IDNET.txt": "project-743aab84-f9a5-4ec7-954.ppp_rico.idnet",
    }
    
    for file_name, table_id in files_to_ingest.items():
        file_path = os.path.join(base_dir, file_name)
        if os.path.exists(file_path):
            ingest_file(client, file_path, table_id)
        else:
            print(f"File not found: {file_path}")

if __name__ == "__main__":
    main()
