from google.cloud import bigquery
import pandas as pd

def check_ca_cocs():
    client = bigquery.Client(project='project-743aab84-f9a5-4ec7-954')
    query = """
    SELECT coc_number, coc_name, pit_count, coc_funding, cps_est, gap 
    FROM `project-743aab84-f9a5-4ec7-954.forensic_layers.national_pipeline_map`
    WHERE state = 'CA'
    """
    try:
        df = client.query(query).to_dataframe()
        print(f"Found {len(df)} CoCs in California.")
        print(f"Total CA PIT Count: {df['pit_count'].sum()}")
        print(f"Total CA Gap: {df['gap'].sum()}")
    except Exception as e:
        print(f"BQ Error: {e}")

if __name__ == '__main__':
    check_ca_cocs()
