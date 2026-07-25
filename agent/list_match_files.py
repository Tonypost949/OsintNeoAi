import json

with open("gdrive_residents_scan.json", "r", encoding="utf-8") as f:
    data = json.load(f)

files = set(item["file_name"] for item in data)
print(f"Total Matches: {len(data)}")
print(f"Unique files: {len(files)}")
print("\nList of unique files:")
for idx, f in enumerate(sorted(list(files))):
    print(f" {idx+1}. {f}")
