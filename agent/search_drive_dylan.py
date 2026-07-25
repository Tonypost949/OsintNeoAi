import json
import re

json_path = "drive_files_list.json"
with open(json_path, "r", encoding="utf-8") as f:
    files = json.load(f)

print(f"Loaded {len(files)} files.")
patterns = [
    re.compile(r"dylan", re.IGNORECASE),
    re.compile(r"garnet", re.IGNORECASE),
    re.compile(r"15822", re.IGNORECASE)
]

matches = []
for file in files:
    name = file["file_name"]
    for pat in patterns:
        if pat.search(name):
            matches.append(file)
            break

print(f"Found {len(matches)} matches:")
for m in matches:
    print(f"- {m['file_name']} (ID: {m['file_id']}, Link: {m['web_view_link']})")
