import os
import csv

csv_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\dl_file_index_20260701T121450Z.csv"
target_terms = ["dsig", "disg", "disgrace", "disgr", "national"]

print("Searching the 6MB dl_file_index CSV...")

matches = []

try:
    with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        print(f"Header: {header}")
        for idx, row in enumerate(reader, 1):
            row_str = " ".join(row)
            row_lower = row_str.lower()
            for term in target_terms:
                if term in row_lower:
                    matches.append(f"Row {idx}: {row_str[:250]}")
                    break
except Exception as e:
    print(f"Error reading CSV: {e}")

print("\n--- CSV SEARCH RESULTS ---")
if matches:
    print(f"Found {len(matches)} occurrences:")
    for m in matches[:50]:
        print(m)
else:
    print("No occurrences found in the CSV.")
