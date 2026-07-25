import re
import json

html_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\.system_generated\steps\855\content.md"

with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Let's find all script blocks that contain "__initData"
init_data_matches = re.findall(r'__initData\s*=\s*(.*?);', content, re.DOTALL)
print(f"Found {len(init_data_matches)} matches for __initData.")

for i, match in enumerate(init_data_matches):
    print(f"\n--- Match {i+1} ---")
    print(f"Length of match: {len(match)}")
    # Write to file to analyze
    filename = f"init_data_{i+1}.txt"
    with open(filename, "w", encoding='utf-8') as out:
        out.write(match)
    print(f"Wrote to {filename}")

    # Let's look for potential Gdrive folder/file elements.
    # Typically, folder contents are inside nested lists.
    # Let's find all string literals (quoted) in the match
    strings = re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"', match)
    print(f"Found {len(strings)} string literals in match {i+1}.")
    
    # Filter for strings that look like drive IDs or names
    drive_id_pattern = re.compile(r'^[a-zA-Z0-9_-]{28,40}$')
    extensions = [".xlsx", ".pdf", ".docx", ".zip", ".png", ".txt", ".jpg", ".csv", ".json", ".rar"]
    
    found_ids = []
    found_filenames = []
    for s in strings:
        if drive_id_pattern.match(s):
            found_ids.append(s)
        if any(ext in s.lower() for ext in extensions):
            found_filenames.append(s)
            
    print(f"Potential Drive IDs ({len(found_ids)}):")
    for fid in set(found_ids[:10]):
        print(f"  - {fid}")
    print(f"Potential Filenames ({len(found_filenames)}):")
    for fn in set(found_filenames):
        print(f"  - {fn}")
