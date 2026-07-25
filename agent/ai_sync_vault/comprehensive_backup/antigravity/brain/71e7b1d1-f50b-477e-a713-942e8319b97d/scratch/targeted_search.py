import os

search_paths = [
    r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d",
    r"C:\Users\HP\OneDrive\Documents\AG2OSINTNEOMAXX",
    r"C:\OSINTNEOAIXL",
    r"C:\OSINT_HB_Data",
    r"C:\OSINT_Investigation_Anthony",
    r"C:\maltego_osint"
]

target_terms = ["disgrace", "national disgrace"]

print("Running fast targeted search for 'disgrace' terms...")

matches = []

for base in search_paths:
    if not os.path.exists(base):
        continue
    print(f"Scanning: {base}")
    for root, dirs, files in os.walk(base):
        if any(p in root for p in ["AppData", "node_modules", ".git", "temp", "tmp", "AomeiRecovery", ".system_generated"]):
            continue
        for f in files:
            if f.endswith(('.txt', '.md', '.csv', '.json', '.html', '.py', '.xlsx', '.xml')):
                fp = os.path.join(root, f)
                try:
                    if f.endswith('.xlsx'):
                        import pandas as pd
                        xl = pd.ExcelFile(fp)
                        for sheet in xl.sheet_names:
                            df = xl.parse(sheet)
                            for r_idx, row in df.iterrows():
                                row_str = " ".join(row.astype(str))
                                for term in target_terms:
                                    if term in row_str.lower():
                                        matches.append(f"EXCEL MATCH in {fp} (Sheet: {sheet}, Row {r_idx}): {row_str}")
                    else:
                        with open(fp, 'r', encoding='utf-8', errors='ignore') as file_obj:
                            for line_num, line in enumerate(file_obj, 1):
                                line_lower = line.lower()
                                for term in target_terms:
                                    if term in line_lower:
                                        matches.append(f"MATCH in {fp} (Line {line_num}): {line.strip()}")
                except Exception as e:
                    pass

print("\n--- TARGETED SEARCH RESULTS ---")
if matches:
    print(f"Found {len(matches)} occurrences:")
    for m in matches:
        print(m)
else:
    print("No occurrences of 'disgrace' found in targeted folders.")
