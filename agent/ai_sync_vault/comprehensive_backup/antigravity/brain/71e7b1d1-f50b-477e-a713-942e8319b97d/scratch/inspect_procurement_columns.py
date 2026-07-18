import pandas as pd
import json

json_path = r"C:\Users\HP\OneDrive\Documents\opencode_work\oc_procurement_projects.json"
index_csv_path = r"C:\Users\HP\OneDrive\Documents\opencode_work\oc_procurement_index.csv"
files_csv_path = r"C:\Users\HP\OneDrive\Documents\opencode_work\oc_procurement_files_index.csv"

print("==================================================")
print("INSPECTING PROCUREMENT DATASET COLUMNS")
print("==================================================\n")

# Inspect JSON
print("1. JSON File:")
try:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"  Total items: {len(data)}")
    if data:
        print("  Keys in first item:", list(data[0].keys()))
        print("  First item preview:")
        print(json.dumps(data[0], indent=2)[:500])
except Exception as e:
    print(f"  Error loading JSON: {e}")

# Inspect Index CSV
print("\n2. Index CSV File:")
try:
    df_index = pd.read_csv(index_csv_path, nrows=5)
    print("  Columns:", df_index.columns.tolist())
    print("  First 2 rows:")
    print(df_index.head(2).to_string())
except Exception as e:
    print(f"  Error loading index CSV: {e}")

# Inspect Files CSV
print("\n3. Files CSV File:")
try:
    df_files = pd.read_csv(files_csv_path, nrows=5)
    print("  Columns:", df_files.columns.tolist())
    print("  First 2 rows:")
    print(df_files.head(2).to_string())
except Exception as e:
    print(f"  Error loading files CSV: {e}")
