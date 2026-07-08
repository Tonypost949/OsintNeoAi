import os
from pathlib import Path
from google.cloud import bigquery
import pandas as pd

PROJECT = "noble-beanbag-497411-m4"
WORK_DIR = Path("C:/Users/HP/OneDrive/Documents/opencode_work")

client = bigquery.Client(project=PROJECT)

full_csv = WORK_DIR / "ppp_rico_ppp_up_to_150k.csv"
table_ref = f"{PROJECT}.ppp_rico.ppp_up_to_150k"

if full_csv.exists():
    print(f"SKIP (exists): ppp_up_to_150k.csv")
else:
    total_rows = client.get_table(table_ref).num_rows
    print(f"Total rows to export: {total_rows}", flush=True)

    chunk_size = 200000
    offset = 0
    first = True

    while offset < total_rows:
        query = f"SELECT * FROM `{table_ref}` LIMIT {chunk_size} OFFSET {offset}"
        df = client.query(query, project=PROJECT).to_dataframe()
        if df.empty:
            break
        df.to_csv(full_csv, mode='w' if first else 'a', header=first, index=False)
        first = False
        offset += len(df)
        print(f"  {offset}/{total_rows}", flush=True)

    print(f"DONE - {offset} rows total")
