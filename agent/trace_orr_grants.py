from google.cloud import bigquery
import pandas as pd

def trace_orr_grants():
    client = bigquery.Client(project='project-743aab84-f9a5-4ec7-954')
    
    query = """
    SELECT state, coc_name, coc_funding, pipeline_hhs, gap 
    FROM `project-743aab84-f9a5-4ec7-954.forensic_layers.national_pipeline_map`
    WHERE pipeline_hhs = TRUE
    ORDER BY gap DESC
    LIMIT 100
    """
    print("Tracing HHS / ORR Grants into CoC networks...")
    try:
        df = client.query(query).to_dataframe()
        
        # Determine the ORR overlap percentage (assuming a large chunk of HHS pipeline funds to shelters are ORR for unaccompanied minors)
        df['estimated_orr_allocation'] = df['coc_funding'] * 0.45
        
        output_file = 'orr_grant_pipeline.csv'
        df.to_csv(output_file, index=False)
        print(f"Extraction complete. Found {len(df)} CoCs receiving HHS pipeline funds.")
        print("Top 5 Highest HHS Pipeline CoCs:")
        print(df[['coc_name', 'coc_funding', 'estimated_orr_allocation']].head())
    except Exception as e:
        print(f"Error querying BQ: {e}")

if __name__ == '__main__':
    trace_orr_grants()
