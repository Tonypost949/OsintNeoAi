import os
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

search_dir = r"c:\Users\HP\OneDrive\Documents\AG2OSINTNEOMAXX"
query = "marshall wu"
feinstein_query = "feinstein"

matches = []

print(f"Scanning {search_dir} recursively for '{query}' or '{feinstein_query}'...")

for root, dirs, files in os.walk(search_dir):
    # Exclude .git and some virtual env dirs if any
    if '.git' in root or '.agents' in root:
        continue
    for file in files:
        if file.endswith(('.txt', '.md', '.json', '.csv', '.log', '.js', '.html')):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        line_lower = line.lower()
                        if query in line_lower or feinstein_query in line_lower:
                            matches.append({
                                'file': file_path,
                                'line_num': line_num,
                                'content': line.strip()
                            })
            except Exception as e:
                # print(f"Error reading {file_path}: {e}")
                pass

print(f"\nScan completed. Found {len(matches)} matches.")
for idx, match in enumerate(matches[:30]):
    print(f"[{idx+1}] File: {match['file']} (Line {match['line_num']})")
    print(f"    Content: {match['content'][:200]}")
