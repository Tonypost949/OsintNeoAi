import os
import json

downloads_path = r"C:\Users\HP\Downloads"
files = ["Dehashed-HBPD-scan.json", "Orange-County-Structural-Failure-Investigation.json"]

for fn in files:
    fp = os.path.join(downloads_path, fn)
    if os.path.exists(fp):
        print(f"\n=== Detailed Inspection: {fn} ===")
        with open(fp, "r", encoding="utf-8") as f:
            data = json.load(f)
            if len(data) > 0:
                item = data[0]
                print("Keys:", list(item.keys()))
                for k, v in item.items():
                    print(f"Key: {k}, Type: {type(v)}")
                    if isinstance(v, (dict, list)):
                        print(f"  Preview of structure: {str(v)[:300]}")
