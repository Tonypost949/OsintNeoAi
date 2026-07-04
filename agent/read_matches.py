import json

with open("detailed_residents_scan.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Total matches found: {len(data)}")
for match in data[:20]:  # print first 20 matches
    print(f"File: {match['file']}, Line: {match['line_num']}")
    print(f"Text: {match['text']}")
    print("-" * 40)
