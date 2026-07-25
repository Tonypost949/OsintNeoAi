import os
import json
import re

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"
files = [
    os.path.join(scratch_dir, "deepseek_data_0", "conversations.json"),
    os.path.join(scratch_dir, "deepseek_data_1", "conversations.json")
]

keywords = ["gilbert", "east st", "covenant", "nunez", "barnes"]

results = []

for idx, fp in enumerate(files):
    if not os.path.exists(fp):
        print(f"File {fp} does not exist!")
        continue
    print(f"Reading {fp} (Size: {os.path.getsize(fp)} bytes)...")
    try:
        with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
            data = json.load(f)
            
        print(f"Loaded JSON from deepseek_data_{idx}. Parsing conversations...")
        for c_idx, conv in enumerate(data):
            title = conv.get("title", "") or "Untitled"
            mapping = conv.get("mapping", {})
            
            # Search title
            for kw in keywords:
                if kw in title.lower():
                    results.append({
                        "file_idx": idx,
                        "conv_idx": c_idx,
                        "title": title,
                        "node_id": "title",
                        "sender": "title",
                        "content": title,
                        "keyword": kw
                    })
            
            # Search messages in mapping
            for node_id, node in mapping.items():
                msg = node.get("message")
                if not msg:
                    continue
                
                sender = msg.get("sender", "unknown")
                fragments = msg.get("fragments", [])
                
                # Try multiple fragment content extraction patterns
                content_parts = []
                for f_item in fragments:
                    if isinstance(f_item, dict):
                        # Pattern 1: type is REQUEST/RESPONSE/THINK and has content
                        f_type = f_item.get("type")
                        f_content = f_item.get("content")
                        if f_content:
                            if isinstance(f_content, dict):
                                parts = f_content.get("parts", [])
                                for p in parts:
                                    content_parts.append(str(p))
                            else:
                                content_parts.append(str(f_content))
                        # Pattern 2: nested mapping or direct values
                        elif "text" in f_item:
                            content_parts.append(str(f_item["text"]))
                    else:
                        content_parts.append(str(f_item))
                
                text = "".join(content_parts)
                if not text:
                    # Try another fallback: look for content directly in msg
                    content_obj = msg.get("content", {})
                    if isinstance(content_obj, dict):
                        parts = content_obj.get("parts", [])
                        text = "".join([str(p) for p in parts])
                    elif isinstance(content_obj, str):
                        text = content_obj
                
                if text:
                    for kw in keywords:
                        if kw in text.lower():
                            results.append({
                                "file_idx": idx,
                                "conv_idx": c_idx,
                                "title": title,
                                "node_id": node_id,
                                "sender": sender,
                                "content": text,
                                "keyword": kw
                            })
                            
    except Exception as e:
        print(f"Error parsing {fp}: {e}")

print(f"\nFound {len(results)} matches for {keywords} in DeepSeek conversations.")

out_path = os.path.join(scratch_dir, "deepseek_investigation_matches.json")
with open(out_path, 'w', encoding='utf-8') as out_f:
    json.dump(results, out_f, indent=2)

print(f"Saved matches to {out_path}.")

# Group and display summaries
summary = {}
for r in results:
    key = (r["file_idx"], r["conv_idx"], r["title"])
    if key not in summary:
        summary[key] = []
    summary[key].append(f"[{r['sender']} - Node {r['node_id']} (Match: {r['keyword']})]: {r['content'][:150]}...")

print("\n--- Summary of Matches by Conversation ---")
for key, msgs in summary.items():
    file_idx, conv_idx, title = key
    print(f"\nFolder {file_idx}, Conv {conv_idx}: '{title}' - {len(msgs)} match(es)")
    for m in msgs[:5]:
        print(f"  {m}")
