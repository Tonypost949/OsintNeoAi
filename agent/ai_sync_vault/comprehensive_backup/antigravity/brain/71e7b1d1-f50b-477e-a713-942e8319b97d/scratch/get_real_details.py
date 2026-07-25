import json
import os

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"
json_path = os.path.join(scratch_dir, "deepseek_investigation_matches.json")
out_path = os.path.join(scratch_dir, "anaheim_details.txt")

if not os.path.exists(json_path):
    print("Matches JSON does not exist!")
    os._exit(1)

with open(json_path, 'r', encoding='utf-8') as f:
    matches = json.load(f)

print(f"Loaded {len(matches)} matches.")

with open(out_path, 'w', encoding='utf-8') as f:
    f.write("ANAHEIM PROPERTY & COVENANT HOUSE TARGET DETAILS\n")
    f.write("================================================\n\n")
    
    for idx, m in enumerate(matches):
        content_lower = m["content"].lower()
        title_lower = m["title"].lower()
        
        # Check if the content or title mentions Gilbert or East St or Covenant
        if "gilbert" in content_lower or "east" in content_lower or "covenant" in content_lower:
            f.write(f"--------------------------------------------------------------------------------\n")
            f.write(f"MATCH #{idx+1} | Folder: {m['file_idx']} | Conv {m['conv_idx']}: {m['title']}\n")
            f.write(f"Sender: {m['sender']} | Node ID: {m['node_id']} | Keyword matched: {m['keyword']}\n")
            f.write(f"--------------------------------------------------------------------------------\n\n")
            f.write(m["content"] + "\n\n")

print(f"Wrote details to {out_path}.")
