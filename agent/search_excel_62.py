import pandas as pd

def search_excel_for_62():
    excel_path = r"c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\osint_20260701T123507Z.xlsx"
    print(f"Reading Excel sheets from: {excel_path}...")
    try:
        xls = pd.ExcelFile(excel_path)
        for sheet_name in xls.sheet_names:
            print(f"Scanning sheet: {sheet_name}...")
            df = pd.read_excel(xls, sheet_name)
            # Find any cells containing "62"
            mask = df.astype(str).apply(lambda x: x.str.contains(r'\b62\b', case=False, na=False)).any(axis=1)
            matches = df[mask]
            if len(matches) > 0:
                print(f"\n🎯 FOUND MATCHES IN SHEET '{sheet_name}':")
                print(matches.head(10).to_string(index=False))
                print("-" * 50)
    except Exception as e:
        print(f"Error scanning Excel: {e}")

if __name__ == "__main__":
    search_excel_for_62()
