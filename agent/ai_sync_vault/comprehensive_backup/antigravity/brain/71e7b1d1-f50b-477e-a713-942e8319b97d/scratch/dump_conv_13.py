import os
import json

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"
conv_file = os.path.join(scratch_dir, "deepseek_data_1", "conversations.json")
out_path = os.path.join(scratch_dir, "conv_13_dump.txt")

with open(conv_file, 'r', encoding='utf-8', errors='ignore') as f:
    data = json.load(f)

conv = data[13]
mapping = conv.get("mapping", {})

ordered_msgs = []
visited = set()

def traverse(node_id):
    if node_id in visited or node_id not in mapping:
        return
    visited.add(node_id)
    node = mapping[node_id]
    msg = node.get("message")
    if msg:
        fragments = msg.get("fragments", [])
        content = ""
        think = ""
        for frag in fragments:
            if frag.get("type") in ["REQUEST", "RESPONSE"]:
                content += frag.get("content", "") or ""
            elif frag.get("type") == "THINK":
                think += frag.get("content", "") or ""
        sender = msg.get("sender", "unknown")
        ordered_msgs.append((sender, content, think))
    
    for child_id in node.get("children", []):
        traverse(child_id)

traverse("root")

if len(ordered_msgs) == 0:
    for node_id, node in mapping.items():
        msg = node.get("message")
        if msg:
            fragments = msg.get("fragments", [])
            content = ""
            think = ""
            for frag in fragments:
                if frag.get("type") in ["REQUEST", "RESPONSE"]:
                    content += frag.get("content", "") or ""
                elif frag.get("type") == "THINK":
                    think += frag.get("content", "") or ""
            ordered_msgs.append((msg.get("sender", "unknown"), content, think))

with open(out_path, 'w', encoding='utf-8') as out_f:
    out_f.write(f"CONVERSATION 13: {conv.get('title')}\n")
    out_f.write("=" * 60 + "\n\n")
    for idx, (s, c, t) in enumerate(ordered_msgs):
        out_f.write(f"--- MESSAGE {idx} | SENDER: {s} ---\n")
        out_f.write(f"CONTENT:\n{c}\n\n")
        if t:
            out_f.write(f"THINKING:\n{t}\n\n")
        out_f.write("=" * 40 + "\n\n")

print(f"Dumped conversation 13 to {out_path}.")
