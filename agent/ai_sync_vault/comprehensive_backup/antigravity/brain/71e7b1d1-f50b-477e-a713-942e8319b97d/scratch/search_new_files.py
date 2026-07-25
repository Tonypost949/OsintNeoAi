import os

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"
new_files = [
    "bigscan.html",
    "ricomermaid.html",
    "OSINT Master Forensic Workbook (1).xlsx",
    "OSINT Master Forensic Workbook.xlsx",
    "WB-2026-001-CA Financial Trace Report.xlsx"
]

target_terms = ["dsig", "disg", "disgrace", "disgr", "national"]

print("Scanning newly copied tablet files...")

matches = []

for fn in new_files:
    fp = os.path.join(scratch_dir, fn)
    if not os.path.exists(fp):
        print(f"File not found: {fn}")
        continue
    print(f"Scanning file: {fn}")
    try:
        if fn.endswith('.xlsx'):
            import pandas as pd
            xl = pd.ExcelFile(fp)
            for sheet in xl.sheet_names:
                df = xl.parse(sheet)
                # Fill na with empty string
                df = df.fillna("")
                for r_idx, row in df.iterrows():
                    # Build string safely
                    row_vals = []
                    for val in row.values:
                        row_vals.append(str(val))
                    row_str = " ".join(row_vals)
                    row_lower = row_str.lower()
                    for term in target_terms:
                        if term in row_lower:
                            matches.append(f"EXCEL MATCH in {fn} (Sheet: {sheet}, Row {r_idx+1}): {row_str[:250]}")
                            break
        else:
            with open(fp, 'r', encoding='utf-8', errors='ignore') as file_obj:
                for line_num, line in enumerate(file_obj, 1):
                    line_lower = line.lower()
                    for term in target_terms:
                        if term in line_lower:
                            matches.append(f"MATCH in {fn} (Line {line_num}): {line.strip()[:200]}")
                            break
    except Exception as e:
        print(f"Error scanning {fn}: {e}")

print("\n--- NEW TABLET FILES SEARCH RESULTS ---")
if matches:
    print(f"Found {len(matches)} occurrences:")
    for m in matches:
        print(m)
else:
    print("No occurrences found in the new tablet files.")
