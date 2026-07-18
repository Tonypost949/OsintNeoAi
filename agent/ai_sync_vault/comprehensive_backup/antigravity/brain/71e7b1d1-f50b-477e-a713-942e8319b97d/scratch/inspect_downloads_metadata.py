import os
import json
import pandas as pd

downloads_path = r"C:\Users\HP\Downloads"
files_to_inspect = [
    "Dehashed-HBPD-scan.json",
    "Orange-County-Structural-Failure-Investigation.json",
    "OSINTNeoAiXXL_chat.json",
    "acrobat.adobe.com_20260624_172521.csv",
    "acrobat.adobe.com_20260624_180025.csv"
]

print("Inspecting Downloads files for BigQuery loading:")
for fn in files_to_inspect:
    fp = os.path.join(downloads_path, fn)
    if os.path.exists(fp):
        print(f"\n--- File: {fn} ({os.path.getsize(fp)} bytes) ---")
        if fn.endswith(".json"):
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    print(f"Data type: {type(data)}")
                    if isinstance(data, dict):
                        print(f"Keys: {list(data.keys())[:10]}")
                        for k, v in list(data.items())[:3]:
                            print(f"  Key '{k}': Type={type(v)}, preview={str(v)[:150]}")
                    elif isinstance(data, list):
                        print(f"Length: {len(data)}")
                        if len(data) > 0:
                            print(f"Sample item type: {type(data[0])}")
                            if isinstance(data[0], dict):
                                print(f"Sample keys: {list(data[0].keys())[:10]}")
            except Exception as e:
                print(f"Error reading JSON: {e}")
        elif fn.endswith(".csv"):
            try:
                df = pd.read_csv(fp)
                print(f"Columns: {list(df.columns)}")
                print(f"Shape: {df.shape}")
                print(df.head(2))
            except Exception as e:
                print(f"Error reading CSV: {e}")
    else:
        print(f"File not found: {fn}")
