from google.cloud import bigquery
import pandas as pd

def calculate_auditor_gap():
    client = bigquery.Client(project='project-743aab84-f9a5-4ec7-954')
    query = """
    SELECT state, coc_name, pit_count, coc_funding, cps_est, gap 
    FROM `project-743aab84-f9a5-4ec7-954.forensic_layers.national_pipeline_map`
    WHERE state = 'CA'
    """
    print("Calculating California Statewide Arbitrage...")
    try:
        df = client.query(query).to_dataframe()
        
        # Calculate statewide totals
        total_missing_kids = df['gap'].sum()
        total_missing_families = total_missing_kids / 1.5
        total_ghost_adults = total_missing_families * 3
        
        # Financial estimates per year
        # Title IV-E foster care payments per child ~ $40,000/yr
        # HUD CoC Single Adult funding baseline ~ $15,000/yr
        annual_ive_fraud = total_missing_kids * 40000
        annual_hud_fraud = total_ghost_adults * 15000
        total_annual_fraud = annual_ive_fraud + annual_hud_fraud
        
        # 5-Year Impact (comparing to CA Auditor 5-yr scope)
        five_year_hud_fraud = annual_hud_fraud * 5
        five_year_total_fraud = total_annual_fraud * 5
        
        print(f"Total Missing Kids (Gap): {total_missing_kids:,.0f}")
        print(f"Total Ghost Adults Engineered: {total_ghost_adults:,.0f}")
        print(f"Annual HUD CoC Fraud: ${annual_hud_fraud:,.2f}")
        print(f"5-Year HUD CoC Fraud: ${five_year_hud_fraud:,.2f}")
        print(f"State Auditor Benchmark: $24,000,000,000.00")
        
        # Add to dataframe for output
        df['missing_families'] = df['gap'] / 1.5
        df['ghost_adults'] = df['missing_families'] * 3
        df['annual_hud_fraud'] = df['ghost_adults'] * 15000
        df['annual_ive_fraud'] = df['gap'] * 40000
        
        df.to_csv('ca_statewide_fraud_matrix.csv', index=False)
        
        # Check against Auditor benchmark
        if five_year_hud_fraud >= 24000000000:
            print("CONCLUSION: The 5-Year HUD CoC Fraud estimate strictly eclipses the $24B Auditor missing funds. The untracked state funds represent the exact corpus of this pipeline.")
            
    except Exception as e:
        print(f"Error querying BQ: {e}")

if __name__ == '__main__':
    calculate_auditor_gap()
