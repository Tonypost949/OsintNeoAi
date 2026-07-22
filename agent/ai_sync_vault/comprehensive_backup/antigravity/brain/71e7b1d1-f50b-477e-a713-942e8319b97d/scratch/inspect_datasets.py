import os
import pandas as pd

datasets = {
    "out_of_state_llc_ppp_network": r"C:\Users\HP\OneDrive\Documents\opencode_work\out_of_state_llc_ppp_network.csv",
    "national_audits_all_state_records": r"C:\Users\HP\OneDrive\Documents\opencode_work\national_audits_all_state_records.csv",
    "HB_Suspicious_LLC_Matrix": r"C:\Users\HP\OneDrive\Documents\opencode_work\HB_Suspicious_LLC_Matrix.csv"
}

for name, path in datasets.items():
    print(f"\n==================== {name} ====================")
    if not os.path.exists(path):
        print(f"File NOT found at: {path}")
        continue
    
    print(f"Path: {path}")
    try:
        # Load a preview and get shape
        df = pd.read_csv(path, nrows=5)
        print("Columns:", list(df.columns))
        
        # Get exact row count efficiently
        total_rows = 0
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            total_rows = sum(1 for line in f) - 1 # exclude header
            
        print(f"Total Rows: {total_rows}")
        
        # Inspect missing values on first 1000 rows as sample or the whole file if small
        full_df = pd.read_csv(path, keep_default_na=False)
        print("Data Quality - Blank values count:")
        for col in full_df.columns:
            blanks = sum(1 for val in full_df[col] if str(val).strip() == "" or str(val).upper() in ("NULL", "N/A", "NONE"))
            print(f"  - {col}: {blanks} blank/null values out of {len(full_df)}")
            
        print("\nFirst 3 rows preview:")
        print(full_df.head(3).to_string())
        
    except Exception as e:
        print(f"Error inspecting file: {e}")
