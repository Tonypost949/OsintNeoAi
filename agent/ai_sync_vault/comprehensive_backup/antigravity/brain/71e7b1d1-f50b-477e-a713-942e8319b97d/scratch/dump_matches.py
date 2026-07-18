import json
import os
import sys

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"
json_path = os.path.join(scratch_dir, "deepseek_investigation_matches.json")
out_txt_path = os.path.join(scratch_dir, "deepseek_investigation_matches_formatted.txt")

if not os.path.exists(json_path):
    print("Matches JSON does not exist!")
    sys.exit(1)

with open(json_path, 'r', encoding='utf-8') as f:
    matches = json.load(f)

print(f"Loaded {len(matches)} matches from JSON.")

# Group matches by conversation
grouped = {}
for m in matches:
    key = (m["file_idx"], m["conv_idx"], m["title"])
    if key not in grouped:
        grouped[key] = []
    grouped[key].append(m)

with open(out_txt_path, 'w', encoding='utf-8') as f:
    f.write("DEEPSEEK CONVERSATION MATCHES DETAILED REPORT\n")
    f.write("=============================================\n\n")
    
    for (file_idx, conv_idx, title), items in sorted(grouped.items()):
        f.write(f"--------------------------------------------------------------------------------\n")
        f.write(f"FOLDER {file_idx} | CONVERSATION {conv_idx}: {title} ({len(items)} matches)\n")
        f.write(f"--------------------------------------------------------------------------------\n\n")
        
        for idx, item in enumerate(items):
            f.write(f"Match #{idx+1} | Sender: {item['sender']} | Node ID: {item['node_id']} | Keyword: {item['keyword']}\n")
            f.write(f"--- CONTENT ---\n")
            f.write(item['content'] + "\n")
            f.write(f"----------------------------------------\n\n")

print(f"Detailed matches saved to {out_txt_path}.")
