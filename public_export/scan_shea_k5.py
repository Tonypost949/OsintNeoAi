import os
import re

search_dirs = [
    r"C:\Users\Amd949609\Downloads",
    r"C:\Users\Amd949609\Documents",
    r"C:\Users\Amd949609\Desktop",
    r"C:\Amd949609_Antigravity_v1",
    r"C:\OsintNeoAi"
]

keywords = ["Shea", "Roundtree", "K5", "K-5", "Sidhu", "Stadium", "Anaheim"]

results = []

for s_dir in search_dirs:
    if not os.path.exists(s_dir):
        continue
    for root, dirs, files in os.walk(s_dir):
        for f in files:
            if f.endswith(('.txt', '.md', '.json', '.csv', '.py', '.html', '.eml')):
                f_path = os.path.join(root, f)
                try:
                    with open(f_path, 'r', encoding='utf-8', errors='ignore') as content:
                        text = content.read()
                        for kw in keywords:
                            if kw.lower() in text.lower():
                                results.append(f"{f_path} -> Keyword match: {kw}")
                                break
                except Exception:
                    pass

out_path = r"C:\Amd949609_Antigravity_v1\tasks\anaheim_evidence_audit\shea_k5_matches.txt"
with open(out_path, 'w', encoding='utf-8') as out:
    for res in results:
        out.write(res + "\n")

print(f"Total keyword match files found: {len(results)}. Saved to {out_path}")
