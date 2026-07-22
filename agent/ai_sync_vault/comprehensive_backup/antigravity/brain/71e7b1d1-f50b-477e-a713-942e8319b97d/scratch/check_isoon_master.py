import pandas as pd

file_path = r"C:\Users\HP\OneDrive\Documents\Master Osint Sheet.xlsx"
print(f"Searching for I-Soon keywords in {file_path} sheets...")

keywords = ["isoon", "i-soon", "anxun", "tele2", "beeline", "kazakhstan", "sichuan"]

try:
    xl = pd.ExcelFile(file_path)
    for sheet in xl.sheet_names:
        df = xl.parse(sheet)
        text = df.astype(str).values.flatten()
        found = []
        for kw in keywords:
            matches = [t for t in text if isinstance(t, str) and kw in t.lower()]
            if matches:
                found.append((kw, len(matches)))
        if found:
            print(f"Sheet '{sheet}': found matches {found}")
except Exception as e:
    print("Error reading sheet:", e)
