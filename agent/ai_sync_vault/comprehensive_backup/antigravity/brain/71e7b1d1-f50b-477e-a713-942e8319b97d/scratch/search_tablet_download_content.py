import os
import re

search_dirs = [
    r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch",
    r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\tablet_downloads"
]

target_terms = ["disgrace", "dsigrace", "dsig", "disg", "national disgrace"]

output_file = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\tablet_matches_utf8.txt"

matches = []

for s_dir in search_dirs:
    if not os.path.exists(s_dir):
        continue
    # Let's search inside the directories recursively
    for root, dirs, files in os.walk(s_dir):
        # Let's skip the directory itself if it is tablet_downloads inside scratch to avoid duplicate paths if there are any
        for f in files:
            fp = os.path.join(root, f)
            if f.endswith(('.txt', '.md', '.json', '.html', '.py', '.csv')):
                try:
                    with open(fp, 'r', encoding='utf-8', errors='ignore') as fo:
                        for line_num, line in enumerate(fo, 1):
                            line_lower = line.lower()
                            for term in target_terms:
                                if term in line_lower:
                                    matches.append((fp, line_num, line.strip()))
                                    break
                except Exception as e:
                    pass

print(f"Found {len(matches)} matches. Writing to {output_file}...")

with open(output_file, 'w', encoding='utf-8') as out:
    for fp, num, text in matches:
        out.write(f"[{fp}:L{num}] {text}\n")

print("Done. Saved matches.")
