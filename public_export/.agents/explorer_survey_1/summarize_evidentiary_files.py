import json
from collections import defaultdict

with open("C:\\OsintNeoAi\\.agents\\explorer_survey_1\\evidentiary_files_list.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for source in ["evidence", "downloads"]:
    print(f"================== {source.upper()} BREAKDOWN ==================")
    items = data[source]
    by_ext = defaultdict(list)
    for item in items:
        by_ext[item["ext"]].append(item)
    
    for ext, file_list in sorted(by_ext.items()):
        total_size = sum(x["size_bytes"] for x in file_list) / (1024*1024)
        print(f"\n--- Ext: {ext} (Count: {len(file_list)}, Total Size: {total_size:.2f} MB) ---")
        for x in file_list[:8]:
            print(f"  - {x['rel_path']} ({x['size_mb']} MB)")
        if len(file_list) > 8:
            print(f"  ... and {len(file_list)-8} more")
