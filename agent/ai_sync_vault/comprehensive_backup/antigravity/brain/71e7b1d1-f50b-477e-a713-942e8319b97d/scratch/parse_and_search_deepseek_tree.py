import os
import json
import re

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"
out_file = os.path.join(scratch_dir, "deepseek_tree_search_results.txt")

# We want to search for disgrace, dsigraCE, national disgrace, city, url, holes, national, etc.
keywords = ["disgrace", "dsigrace", "dsigraCE", "national", "url", "city", "cities", "hole"]

results = []

for idx in [0, 1]:
    d = os.path.join(scratch_dir, f"deepseek_data_{idx}")
    conv_file = os.path.join(d, "conversations.json")
    if not os.path.exists(conv_file):
        print(f"File {conv_file} does not exist!")
        continue
    
    print(f"Parsing nested tree structure for deepseek_data_{idx}...")
    try:
        with open(conv_file, 'r', encoding='utf-8', errors='ignore') as f:
            data = json.load(f)
            
        for c_idx, conv in enumerate(data):
            title = conv.get("title", "") or "Untitled"
            mapping = conv.get("mapping", {})
            
            # Reconstruct the messages chronologically or just scan all nodes in mapping
            conv_texts = []
            for node_id, node in mapping.items():
                msg = node.get("message")
                if not msg:
                    continue
                
                # Extract text content from fragments
                fragments = msg.get("fragments", [])
                node_text = ""
                for frag in fragments:
                    if frag.get("type") in ["REQUEST", "RESPONSE", "THINK"]:
                        node_text += frag.get("content", "") or ""
                
                if node_text:
                    conv_texts.append((msg.get("sender", "unknown"), node_text))
            
            # Search the reconstructed texts
            for sender, text in conv_texts:
                for kw in keywords:
                    if re.search(r'\b' + re.escape(kw) + r'\b', text, re.IGNORECASE) or kw.lower() in text.lower():
                        results.append({
                            "folder_idx": idx,
                            "conv_idx": c_idx,
                            "title": title,
                            "sender": sender,
                            "text": text,
                            "keyword": kw
                        })
                        break
                        
    except Exception as e:
        print(f"Error parsing deepseek_data_{idx}: {e}")

print(f"Total matches found in nested tree: {len(results)}")

# Group matches by conversation to show the context nicely
matches_by_conv = {}
for r in results:
    key = (r["folder_idx"], r["conv_idx"], r["title"])
    if key not in matches_by_conv:
        matches_by_conv[key] = []
    matches_by_conv[key].append(r)

with open(out_file, 'w', encoding='utf-8') as out_f:
    out_f.write(f"Nested DeepSeek Tree Search Results\n")
    out_f.write(f"===================================\n\n")
    for key, matches in matches_by_conv.items():
        folder_idx, conv_idx, title = key
        out_f.write(f"=========================================\n")
        out_f.write(f"FOLDER {folder_idx} | CONVERSATION {conv_idx}: {title}\n")
        out_f.write(f"=========================================\n")
        
        # Write some of the matches or the whole dialogue of the matching conversation
        # Let's write the whole conversation if there's a match, so we have the full context!
        # Reconstruct conversation messages chronologically by mapping's parent-child links if possible, 
        # or just print all unique non-empty messages
        d = os.path.join(scratch_dir, f"deepseek_data_{folder_idx}")
        conv_file = os.path.join(d, "conversations.json")
        try:
            with open(conv_file, 'r', encoding='utf-8', errors='ignore') as f:
                data = json.load(f)
            conv = data[conv_idx]
            mapping = conv.get("mapping", {})
            
            # Simple chronological sort: start at root and traverse down
            # Often root node has id "root"
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
            
            # If traverse didn't find everything (e.g. root wasn't named "root"), do fallback
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
            
            for s, c, t in ordered_msgs:
                out_f.write(f"[{s}]:\n{c}\n")
                if t:
                    out_f.write(f"  (Thinking: {t[:200]}...)\n")
                out_f.write("-" * 40 + "\n")
                
        except Exception as e:
            out_f.write(f"Error reconstructing conversation: {e}\n")
        out_f.write("\n\n")

print(f"Saved matched conversations to {out_file}.")

# Let's print out the titles of matched conversations to console safely
print("\n--- MATCHED CONVERSATIONS ---")
for key in matches_by_conv.keys():
    folder_idx, conv_idx, title = key
    title_safe = title.encode('ascii', 'backslashreplace').decode('ascii')
    print(f"Folder {folder_idx}, Conv {conv_idx}: '{title_safe}'")
