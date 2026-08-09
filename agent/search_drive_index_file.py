import json
import re

json_path = "drive_files_list.json"
print("Loading drive_files_list.json...")
with open(json_path, "r", encoding="utf-8") as f:
    files = json.load(f)

print(f"Loaded {len(files)} files. Searching for relevant audit reports...")

patterns = [
    re.compile(r"weaver", re.IGNORECASE),
    re.compile(r"andrew.*do", re.IGNORECASE),
    re.compile(r"do.*forensic", re.IGNORECASE),
    re.compile(r"forensic.*audit", re.IGNORECASE),
    re.compile(r"phase.*1.*audit", re.IGNORECASE),
    re.compile(r"county.*contract.*audit", re.IGNORECASE),
]

matches = []
for file in files:
    name = file["file_name"]
    for pat in patterns:
        if pat.search(name):
            matches.append(file)
            break

# Print matches
print(f"Found {len(matches)} potential matches:")
for m in sorted(matches, key=lambda x: x["file_name"]):
    print(f"- Name: {m['file_name']}")
    print(f"  ID: {m['file_id']}")
    print(f"  Mime: {m['mime_type']}")
    print(f"  Modified: {m['modified_time']}")
    print(f"  Owners: {m['owner_emails']}")
    print(f"  Link: {m['web_view_link']}")
    print("-" * 50)
