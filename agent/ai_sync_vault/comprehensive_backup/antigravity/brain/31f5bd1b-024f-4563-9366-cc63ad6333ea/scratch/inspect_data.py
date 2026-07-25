import pandas as pd
import json

paths = {
    'out_of_state_llc_ppp_network': r'C:\Users\HP\OneDrive\Documents\opencode_work\out_of_state_llc_ppp_network.csv',
    'national_audits_all_state_records': r'C:\Users\HP\OneDrive\Documents\opencode_work\national_audits_all_state_records.csv',
    'HB_Suspicious_LLC_Matrix': r'C:\Users\HP\OneDrive\Documents\opencode_work\HB_Suspicious_LLC_Matrix.csv'
}

for name, path in paths.items():
    print(f"\n==================================================")
    print(f"FILE: {name}")
    print(f"PATH: {path}")
    print(f"==================================================")
    
    df = pd.read_csv(path)
    print(f"Row count: {len(df)}")
    print(f"Columns and types:")
    for col in df.columns:
        null_count = df[col].isnull().sum()
        unique_count = df[col].nunique()
        sample_vals = df[col].dropna().head(2).tolist()
        print(f"  - {col} ({df[col].dtype}): {null_count} nulls, {unique_count} unique, sample: {sample_vals}")
