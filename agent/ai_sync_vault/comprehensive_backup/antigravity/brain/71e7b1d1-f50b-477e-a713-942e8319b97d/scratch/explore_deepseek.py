import os
import json

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"

for idx in [0, 1]:
    d = os.path.join(scratch_dir, f"deepseek_data_{idx}")
    print(f"\n=========================================")
    print(f"FILES IN deepseek_data_{idx}:")
    if not os.path.exists(d):
        print("Directory does not exist!")
        continue
    for root, dirs, files in os.walk(d):
        for f in files:
            p = os.path.join(root, f)
            print(f"  {os.path.relpath(p, d)} (Size: {os.path.getsize(p)} bytes)")
            
    conv_file = os.path.join(d, "conversations.json")
    if os.path.exists(conv_file):
        try:
            with open(conv_file, 'r', encoding='utf-8', errors='ignore') as f:
                data = json.load(f)
            print(f"\nCONVERSATION TITLES IN deepseek_data_{idx} ({len(data)} total):")
            for c_idx, conv in enumerate(data):
                title = conv.get("title", "Untitled")
                msg_count = len(conv.get("messages", []))
                print(f"  [{c_idx}] {title} ({msg_count} messages)")
        except Exception as e:
            print(f"Error reading conversations: {e}")
