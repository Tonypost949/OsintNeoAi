import json
import os
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

results_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\marshall_wu_search_results.json"
output_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\marshall_wu_detailed_bodies.txt"

if not os.path.exists(results_path):
    print(f"File not found: {results_path}")
    exit(1)

with open(results_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Collect all messages where Marshall Wu is the sender or direct recipient
wu_messages = []
for msg in data:
    frm = msg.get('from', '').lower()
    to = msg.get('to', '').lower()
    subject = msg.get('subject', '').lower()
    body = msg.get('body', '')
    snippet = msg.get('snippet', '')
    
    # We want to pull out actual emails from Marshall Wu, or direct emails to him
    if 'marshall_wu' in frm or 'marshall_wu' in to or 'wu, marshall' in frm or 'wu, marshall' in to:
        wu_messages.append(msg)

# Sort by date
def parse_date(d_str):
    # simple sorting helper
    return d_str or ""

wu_messages.sort(key=lambda x: parse_date(x.get('date')))

lines = []
lines.append(f"TOTAL DIRECT EMAILS CONCERNING MARSHALL WU: {len(wu_messages)}\n")

for idx, msg in enumerate(wu_messages):
    lines.append("="*80)
    lines.append(f"EMAIL [{idx+1}]")
    lines.append(f"Folder: {msg.get('folder', 'Unknown')}")
    lines.append(f"Date: {msg.get('date')}")
    lines.append(f"From: {msg.get('from')}")
    lines.append(f"To: {msg.get('to')}")
    lines.append(f"Subject: {msg.get('subject')}")
    lines.append("-"*40)
    
    body = msg.get('body', '')
    if not body:
        body = msg.get('snippet', '[No Body Content]')
    
    lines.append(body.strip())
    lines.append("="*80 + "\n")

with open(output_path, 'w', encoding='utf-8') as out_f:
    out_f.write("\n".join(lines))

print(f"Detailed bodies written to {output_path}. Total messages: {len(wu_messages)}")
