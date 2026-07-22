import os
import pandas as pd

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"
excel_files = [f for f in os.listdir(scratch_dir) if f.endswith(".xlsx")]

print(f"Found Excel files: {excel_files}")

for f in excel_files:
    path = os.path.join(scratch_dir, f)
    try:
        xl = pd.ExcelFile(path)
        for sheet in xl.sheet_names:
            df = pd.read_excel(path, sheet_name=sheet)
            # Find rows where any cell contains 'Gilbert' or '632' or '213' or 'East' or 'Covenant'
            mask = df.astype(str).apply(lambda x: x.str.contains("Gilbert|East St|Covenant|213|632", case=False, na=False))
            matches = df[mask.any(axis=1)]
            if len(matches) > 0:
                print(f"\n=========================================")
                print(f"FILE: {f} | SHEET: {sheet}")
                print(f"Columns: {list(df.columns)}")
                print(f"Matches count: {len(matches)}")
                # Show first few matching rows with select columns or just the full rows
                for idx, row in matches.iterrows():
                    print(f"\nRow {idx}:")
                    for col in df.columns:
                        val = row[col]
                        if pd.notna(val) and any(term in str(val).lower() for term in ["gilbert", "east", "covenant", "213", "632"]):
                            print(f"  {col}: {val}")
                        elif pd.notna(val) and len(str(val)) < 100:
                            print(f"  {col}: {val}")
    except Exception as e:
        print(f"Error reading {f}: {e}")
