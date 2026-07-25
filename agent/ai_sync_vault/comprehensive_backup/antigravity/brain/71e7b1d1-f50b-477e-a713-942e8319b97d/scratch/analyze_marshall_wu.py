import json
import os
import sys

# Reconfigure stdout just in case
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

results_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\marshall_wu_search_results.json"
output_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\marshall_wu_analysis.txt"

if not os.path.exists(results_path):
    print(f"File not found: {results_path}")
    exit(1)

with open(results_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

lines = []
lines.append(f"Data type: {type(data)}")
if isinstance(data, list):
    lines.append(f"Total messages: {len(data)}")
    all_msgs = data
else:
    lines.append(f"Total folders: {list(data.keys())}")
    all_msgs = []
    for folder, messages in data.items():
        for m in messages:
            m['folder'] = folder
            all_msgs.append(m)

lines.append("\n--- ALL MATCHING EMAILS ---")
for idx, msg in enumerate(all_msgs):
    lines.append(f"\n[{idx+1}] Folder: {msg.get('folder', 'Unknown')} | Date: {msg.get('date')}")
    lines.append(f"From: {msg.get('from')} | To: {msg.get('to')}")
    lines.append(f"Subject: {msg.get('subject')}")
    snippet = msg.get('snippet', '')
    if not snippet and 'body' in msg:
        snippet = msg['body'][:300]
    lines.append(f"Snippet: {snippet}")

lines.append("\n--- SENDER STATS ---")
from_counts = {}
for msg in all_msgs:
    sender = msg.get('from', 'Unknown')
    from_counts[sender] = from_counts.get(sender, 0) + 1
for sender, count in sorted(from_counts.items(), key=lambda x: x[1], reverse=True):
    lines.append(f"{sender}: {count}")

# Write to file
with open(output_path, 'w', encoding='utf-8') as out_f:
    out_f.write("\n".join(lines))

print(f"Analysis written successfully to {output_path}")
