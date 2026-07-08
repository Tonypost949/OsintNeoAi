import os
from pathlib import Path
from google.cloud import bigquery
import pandas as pd

PROJECT = "noble-beanbag-497411-m4"
WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")

client = bigquery.Client(project=PROJECT)

csv_path = WORK_DIR / "ppp_rico_ppp_up_to_150k.csv"
table_ref = f"{PROJECT}.ppp_rico.ppp_up_to_150k"
total_rows = client.get_table(table_ref).num_rows

existing_rows = 0
if csv_path.exists():
    with open(csv_path, 'r') as f:
        existing_rows = sum(1 for _ in f) - 1

print(f"Resuming from row {existing_rows} of {total_rows}")

chunk_size = 500000
offset = existing_rows
first = False

while offset < total_rows:
    print(f"Fetching offset {offset}...", flush=True)
    query = f"SELECT * FROM `{table_ref}` LIMIT {chunk_size} OFFSET {offset}"
    df = client.query(query, project=PROJECT).to_dataframe()
    if df.empty:
        break
    df.to_csv(csv_path, mode='a', header=False, index=False)
    offset += len(df)
    print(f"  {offset}/{total_rows}", flush=True)

print(f"DONE - {offset} rows total")
