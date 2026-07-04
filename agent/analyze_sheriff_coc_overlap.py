from google.cloud import bigquery
import pandas as pd

def analyze_sheriff_coc():
    client = bigquery.Client(project='project-743aab84-f9a5-4ec7-954')
    
    query = """
    SELECT state, coc_number, coc_name, pit_count, coc_funding, cps_est, gap 
    FROM `project-743aab84-f9a5-4ec7-954.forensic_layers.national_pipeline_map`
    WHERE LOWER(coc_name) LIKE '%county%'
    ORDER BY gap DESC
    LIMIT 100
    """
    print("Executing Sheriff/County CoC Overlap Analysis...")
    try:
        df = client.query(query).to_dataframe()
        
        # We classify County CoCs as high-risk for Sheriff-only contracted jurisdiction fraud 
        # (where local PDs don't exist and Sheriffs manage unincorporated zones).
        df['jurisdiction_type'] = 'County/Sheriff'
        df['risk_multiplier'] = 1.5
        df['adjusted_estimated_leakage'] = df['gap'] * 20000 # Estimate IV-E + HUD fraud dollars per missing child per year
        
        output_file = 'sheriff_coc_risk_matrix.csv'
        df.to_csv(output_file, index=False)
        print(f"Analysis complete. Extracted {len(df)} County-level CoCs to {output_file}")
        print("Top 5 Highest Risk Sheriff-Contract CoCs:")
        print(df[['coc_name', 'gap', 'adjusted_estimated_leakage']].head())
    except Exception as e:
        print(f"Error querying BQ: {e}")

if __name__ == '__main__':
    analyze_sheriff_coc()
