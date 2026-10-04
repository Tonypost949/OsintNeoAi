import pandas as pd
import json

def trace_tribal_trustees():
    print("Parsing tribal_unclaimed_matches.csv...")
    try:
        # Load the CSV
        df = pd.read_csv('tribal_unclaimed_matches.csv')
        
        # Look for hispanic or indigenous sounding surnames from the decedent_or_heir_name
        # In CA Unclaimed property, many conservatorship / trust accounts list the county or a fiduciary.
        # We will extract rows where amount is > $1000 and it's in a known Sheriff/CoC jurisdiction (like Orange County)
        df['county'] = df['county'].fillna('UNKNOWN').astype(str)
        df_target = df[(df['county'].str.contains('ORANGE', case=False)) | (df['county'].str.contains('LOS ANGELES', case=False)) | (df['county'].str.contains('SAN DIEGO', case=False))]
        
        print(f"Found {len(df_target)} records in Southern California jurisdictions (OC, LA, SD).")
        
        # Sort by amount (descending)
        if 'amount_1' in df_target.columns:
            df_target['amount_1'] = pd.to_numeric(df_target['amount_1'], errors='coerce').fillna(0)
            df_target = df_target.sort_values(by='amount_1', ascending=False)
        
        output_file = 'tribal_trustees_socal.csv'
        df_target.to_csv(output_file, index=False)
        print(f"Extracted trustees to {output_file}")
        
        print("Top 5 Highest Value Target Estates:")
        print(df_target[['decedent_or_heir_name', 'county', 'amount_1']].head(10))
        
    except Exception as e:
        print(f"Error parsing CSV: {e}")

if __name__ == '__main__':
    trace_tribal_trustees()
