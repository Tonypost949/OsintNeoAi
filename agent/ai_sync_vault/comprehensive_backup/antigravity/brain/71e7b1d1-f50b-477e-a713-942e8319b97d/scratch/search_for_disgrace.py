import os
import re

search_paths = [
    r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d",
    r"C:\Users\HP\OneDrive\Documents\AG2OSINTNEOMAXX",
    r"C:\OSINTNEOAIXL",
    r"C:\OSINT_HB_Data",
    r"C:\OSINT_Investigation_Anthony",
    r"C:\maltego_osint",
    r"C:\Users\HP\OneDrive\Documents"
]

target_terms = ["disgrace", "national disgrace", "disgr"]

print("Searching for terms related to 'disgrace' across all folders...")

matches = []

for base in search_paths:
    if not os.path.exists(base):
        continue
    print(f"Searching in: {base}")
    for root, dirs, files in os.walk(base):
        # Skip standard system directories
        if any(p in root for p in ["AppData", "node_modules", ".git", "temp", "tmp", "AomeiRecovery"]):
            continue
        for f in files:
            # Only search text-based files or spreadsheet files for speed
            if f.endswith(('.txt', '.md', '.csv', '.json', '.html', '.py', '.xlsx', '.xml')):
                fp = os.path.join(root, f)
                try:
                    if f.endswith('.xlsx'):
                        # Quick check for xlsx sheet contents
                        import pandas as pd
                        xl = pd.ExcelFile(fp)
                        for sheet in xl.sheet_names:
                            df = xl.parse(sheet)
                            text_block = df.astype(str).values.flatten()
                            for row_text in text_block:
                                for term in target_terms:
                                    if term in str(row_text).lower():
                                        matches.append(f"EXCEL MATCH in {fp} (Sheet: {sheet}): '{row_text}'")
                    else:
                        with open(fp, 'r', encoding='utf-8', errors='ignore') as file_obj:
                            for line_num, line in enumerate(file_obj, 1):
                                line_lower = line.lower()
                                for term in target_terms:
                                    if term in line_lower:
                                        matches.append(f"TEXT MATCH in {fp} (Line {line_num}): '{line.strip()}'")
                except Exception as e:
                    pass

print("\n--- SEARCH RESULTS ---")
if matches:
    print(f"Found {len(matches)} occurrences:")
    for m in matches[:50]: # Show first 50 matches
        print(m)
else:
    print("No occurrences of 'disgrace' found in any of the checked directories.")
