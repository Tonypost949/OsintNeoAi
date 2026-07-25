import os
import json
import re

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"
out_file = os.path.join(scratch_dir, "deepseek_full_matches.txt")

keywords = [r"disgrace", r"dsigrace", r"dsigraCE", r"national", r"url", r"city", r"cities", r"hole"]

matches_found = []

with open(out_file, 'w', encoding='utf-8') as out:
    for idx in [0, 1]:
        d = os.path.join(scratch_dir, f"deepseek_data_{idx}")
        conv_file = os.path.join(d, "conversations.json")
        if not os.path.exists(conv_file):
            continue
        
        out.write(f"\n=========================================\n")
        out.write(f"SCANNING FOLDER: deepseek_data_{idx}\n")
        out.write(f"=========================================\n")
        
        try:
            with open(conv_file, 'r', encoding='utf-8', errors='ignore') as f:
                data = json.load(f)
            
            for c_idx, conv in enumerate(data):
                title = conv.get("title", "Untitled")
                messages = conv.get("messages", [])
                
                # Check if any message contains our keywords
                has_kw = False
                for msg in messages:
                    content = msg.get("content", "") or ""
                    for kw in keywords:
                        if re.search(kw, content, re.IGNORECASE):
                            has_kw = True
                            break
                    if has_kw:
                        break
                
                if has_kw:
                    out.write(f"\n--- CONVERSATION {c_idx}: {title} ---\n")
                    for m_idx, msg in enumerate(messages):
                        sender = msg.get("sender", "unknown")
                        content = msg.get("content", "") or ""
                        out.write(f"[{sender}]: {content}\n\n")
                    matches_found.append((idx, c_idx, title))
        except Exception as e:
            out.write(f"Error reading deepseek_data_{idx}: {e}\n")

print(f"Scanned deepseek data. Found {len(matches_found)} conversations with keyword references.")
print(f"Full conversation content saved to {out_file}.")
for idx, c_idx, title in matches_found[:20]:
    title_safe = title.encode('ascii', 'backslashreplace').decode('ascii')
    print(f"  Folder {idx}, Conv {c_idx}: {title_safe}")
