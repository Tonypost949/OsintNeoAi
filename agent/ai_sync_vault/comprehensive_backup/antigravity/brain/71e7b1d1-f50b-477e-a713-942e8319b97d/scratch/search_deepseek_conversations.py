import os
import json
import re

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"

files = [
    os.path.join(scratch_dir, "deepseek_data_0", "conversations.json"),
    os.path.join(scratch_dir, "deepseek_data_1", "conversations.json")
]

keywords = ["disgrace", "dsigrace", "disg", "dsig", "national disgrace"]

print("Searching DeepSeek conversations for disgrace/dsigrace/disg/dsig/national disgrace...")

results = []

for idx, fp in enumerate(files):
    if not os.path.exists(fp):
        print(f"File {fp} does not exist!")
        continue
    print(f"Reading {fp} (Size: {os.path.getsize(fp)} bytes)...")
    try:
        with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
            data = json.load(f)
            
        print(f"Loaded JSON. Parsing conversations...")
        # Since it's deepseek export, it should be a list of conversations
        # Each conversation has a title and messages
        for conv in data:
            title = conv.get("title", "")
            # Check title for keywords
            for kw in keywords:
                if kw in title.lower():
                    results.append((idx, title, "Conversation Title Match", title))
                    break
            
            # Check messages
            messages = conv.get("messages", [])
            for msg in messages:
                content = msg.get("content", "")
                if not content:
                    continue
                for kw in keywords:
                    if kw in content.lower():
                        results.append((idx, title, msg.get("sender", "unknown"), content))
                        break
    except Exception as e:
        print(f"Error parsing {fp}: {e}")

print(f"\nFound {len(results)} matches in DeepSeek conversations.")

out_path = os.path.join(scratch_dir, "deepseek_search_results_utf8.txt")
with open(out_path, 'w', encoding='utf-8') as out_f:
    for f_idx, title, sender, content in results:
        out_f.write(f"=== DEEPSEEK EXPORT {f_idx} | CONVERSATION: {title} | SENDER: {sender} ===\n")
        out_f.write(content + "\n\n")

print(f"Saved results to {out_path}.")

# Print the context of first few matches safely using repr() or backslashreplace
for f_idx, title, sender, content in results[:30]:
    # Find matching lines or print snippet
    print(f"--- MATCH IN '{title}' (Sender: {sender}) ---")
    snippet = content[:300].replace('\n', ' ')
    safe_snip = snippet.encode('ascii', 'backslashreplace').decode('ascii')
    print(safe_snip)
