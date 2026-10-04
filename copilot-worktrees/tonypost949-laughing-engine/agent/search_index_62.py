import pandas as pd

def search_index_for_62():
    csv_path = r"c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\dl_file_index_20260701T123507Z.csv"
    print(f"Reading local index file: {csv_path}...")
    try:
        df = pd.read_csv(csv_path)
        print(f"Total files indexed: {len(df)}")
        
        # Search all columns for the number 62 or "62"
        # We look for rows where any cell contains '62' (as a string or number)
        mask = df.astype(str).apply(lambda x: x.str.contains(r'\b62\b', case=False, na=False)).any(axis=1)
        matches = df[mask]
        
        if len(matches) > 0:
            print("\n=== MATCHING FILES IN LOCAL SCAN INDEX ===")
            print(matches.to_string(index=False))
        else:
            # Let's print the first 10 files to see what is there
            print("\n=== SAMPLE ENTRIES (FIRST 10) ===")
            print(df.head(10).to_string(index=False))
    except Exception as e:
        print(f"Error reading CSV index: {e}")

if __name__ == "__main__":
    search_index_for_62()
