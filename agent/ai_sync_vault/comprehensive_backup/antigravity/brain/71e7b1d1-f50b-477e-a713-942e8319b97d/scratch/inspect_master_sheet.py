import pandas as pd

file_path = r"C:\Users\HP\OneDrive\Documents\Master Osint Sheet.xlsx"
print(f"Reading {file_path} sheets...")
try:
    xl = pd.ExcelFile(file_path)
    print("Sheets in Master Osint Sheet:", xl.sheet_names)
    for sheet in xl.sheet_names:
        df = xl.parse(sheet)
        print(f"\nSheet '{sheet}' shape: {df.shape}")
        print("Columns:", list(df.columns)[:15])
        print("First 2 rows:")
        print(df.head(2).to_string())
except Exception as e:
    print("Error reading master sheet:", e)
