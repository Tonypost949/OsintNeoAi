import json
import re

with open("gdrive_residents_scan.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Total entries in Google Drive matches: {len(data)}")

# Let's see unique file names
files = set(item["file_name"] for item in data)
print(f"Files scanned with matches: {list(files)}")

# Let's extract names from the match texts
name_pattern = re.compile(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b')
unique_names = set()
for item in data:
    text = item["text"]
    for match in name_pattern.finditer(text):
        name = match.group(0)
        # Filter out obvious false positives
        if not any(noise in name for noise in ["Google", "Drive", "Report", "Search", "Results", "Help", "Support", "Contact", "Dashboard", "Log", "Error", "System", "File", "Date", "Time", "Mime", "Bytes"]):
            unique_names.add(name)

print(f"\nUnique Names Extracted ({len(unique_names)}):")
for name in sorted(list(unique_names))[:100]:
    print(f" - {name}")
