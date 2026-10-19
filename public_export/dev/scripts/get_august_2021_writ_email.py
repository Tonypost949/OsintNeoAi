import json
import csv
from pathlib import Path

root = Path(r'C:\OsintNeoAi')
json_file = root / 'archive' / 'OsintNeoAi-Copy-1' / 'gmail_amd949609_hits.json'

if json_file.exists():
    data = json.loads(json_file.read_text(encoding='utf-8', errors='ignore'))
    print(f"Total Gmail records in archive: {len(data)}")
    aug_hits = []
    for item in data:
        item_str = json.dumps(item).lower()
        if '2021' in item_str and ('08' in item_str or 'aug' in item_str) and ('writ' in item_str or 'stay' in item_str or 'ex parte' in item_str or 'luege' in item_str):
            aug_hits.append(item)
    print(f"Found {len(aug_hits)} August 2021 Writ/Stay/Ex Parte Gmail hits:\n")
    for idx, h in enumerate(aug_hits):
        print(f"--- MATCH #{idx+1} ---")
        print(f"ID: {h.get('id')}")
        print(f"Date: {h.get('date')}")
        print(f"From: {h.get('from_user')}")
        print(f"Subject: {h.get('subject')}")
        print(f"Snippet: {h.get('snippet')}\n")
else:
    print(f"File not found: {json_file}")
