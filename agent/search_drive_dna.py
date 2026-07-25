import json
import re

json_path = "drive_files_list.json"
with open(json_path, "r", encoding="utf-8") as f:
    files = json.load(f)

patterns = [
    re.compile(r"dna", re.IGNORECASE),
    re.compile(r"ima loa", re.IGNORECASE)
]

matches = []
for file in files:
    name = file["file_name"]
    for pat in patterns:
        if pat.search(name):
            matches.append(file)
            break

print(f"Found {len(matches)} files:")
for m in matches[:30]:
    print(f"- {m['file_name']} (ID: {m['file_id']}, Link: {m['web_view_link']})")
