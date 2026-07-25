import os
import pandas as pd
import re

try:
    import docx
except ImportError:
    # If python-docx is not installed, we can try to install it or read XML directly from the zip container of .docx
    pass

search_dirs = [
    r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch",
    r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\tablet_downloads"
]

target_terms = ["disgrace", "dsigrace", "dsig", "disg"]

print("Scanning Excel and Word documents in scratch and tablet_downloads for disgrace/dsigrace/disg/dsig...")

excel_matches = []
docx_matches = []

for s_dir in search_dirs:
    if not os.path.exists(s_dir):
        continue
    for root, dirs, files in os.walk(s_dir):
        for f in files:
            fp = os.path.join(root, f)
            if f.endswith('.xlsx'):
                try:
                    xl = pd.ExcelFile(fp)
                    for sheet in xl.sheet_names:
                        df = xl.parse(sheet)
                        # Search each cell in the df
                        for row_idx, row in df.iterrows():
                            for col_idx, val in enumerate(row):
                                val_str = str(val)
                                for term in target_terms:
                                    if term in val_str.lower():
                                        excel_matches.append((fp, sheet, row_idx, df.columns[col_idx], val_str))
                                        break
                except Exception as e:
                    pass
            elif f.endswith('.docx'):
                # Try to read docx as a zip file containing word/document.xml to avoid dependencies
                try:
                    import zipfile
                    with zipfile.ZipFile(fp) as z:
                        doc_xml = z.read("word/document.xml").decode("utf-8")
                        # Strip XML tags to get clean text
                        text_content = re.sub(r'<[^>]+>', ' ', doc_xml)
                        for term in target_terms:
                            # Find matches
                            matches_found = list(re.finditer(term, text_content, re.IGNORECASE))
                            if matches_found:
                                docx_matches.append((fp, term, len(matches_found)))
                except Exception as e:
                    pass

print(f"\nExcel matches found: {len(excel_matches)}")
for fp, sheet, r, c, val in excel_matches[:30]:
    print(f"[{os.path.basename(fp)} -> Sheet: {sheet}, Row {r}, Col {c}]: {val[:150]}")

print(f"\nDocx matches found: {len(docx_matches)}")
for fp, term, count in docx_matches:
    print(f"[{os.path.basename(fp)}]: Found {count} occurrences of '{term}'")
