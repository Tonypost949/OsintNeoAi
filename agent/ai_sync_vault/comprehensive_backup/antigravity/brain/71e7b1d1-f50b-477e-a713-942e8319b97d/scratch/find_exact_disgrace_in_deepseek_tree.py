import os
import json
import re

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"

target_terms = ["disgrace", "dsigra", "national disgrace"]

results = []

for idx in [0, 1]:
    d = os.path.join(scratch_dir, f"deepseek_data_{idx}")
    conv_file = os.path.join(d, "conversations.json")
    if not os.path.exists(conv_file):
        continue
    
    try:
        with open(conv_file, 'r', encoding='utf-8', errors='ignore') as f:
            data = json.load(f)
            
        for c_idx, conv in enumerate(data):
            title = conv.get("title", "") or "Untitled"
            mapping = conv.get("mapping", {})
            
            for node_id, node in mapping.items():
                msg = node.get("message")
                if not msg:
                    continue
                
                fragments = msg.get("fragments", [])
                node_text = ""
                for frag in fragments:
                    if frag.get("type") in ["REQUEST", "RESPONSE", "THINK"]:
                        node_text += frag.get("content", "") or ""
                
                for term in target_terms:
                    if term.lower() in node_text.lower():
                        results.append({
                            "folder": idx,
                            "conv_idx": c_idx,
                            "title": title,
                            "sender": msg.get("sender", "unknown"),
                            "text": node_text,
                            "term": term
                        })
    except Exception as e:
        print(f"Error parsing deepseek_data_{idx}: {e}")

print(f"Found {len(results)} exact disgrace matches in tree.")
for r in results:
    title_safe = r["title"].encode('ascii', 'backslashreplace').decode('ascii')
    print(f"\n=========================================")
    print(f"FOLDER {r['folder']} | CONV {r['conv_idx']}: {title_safe} | SENDER: {r['sender']} | TERM: {r['term']}")
    print(f"=========================================")
    # Print the lines containing the term
    lines = r["text"].split('\n')
    for line in lines:
        if r['term'].lower() in line.lower():
            line_safe = line.encode('ascii', 'backslashreplace').decode('ascii')
            print(f"Line: {line_safe}")
