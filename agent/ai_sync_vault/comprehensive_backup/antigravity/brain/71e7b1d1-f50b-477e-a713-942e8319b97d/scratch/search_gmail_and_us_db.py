import os
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

search_dirs = [
    r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d",
    r"c:\Users\HP\OneDrive\Documents\AG2OSINTNEOMAXX"
]

targets = ["amd949609", "gmail", "database", "american"]

print("Starting deep recursive search...")
found_count = 0

for s_dir in search_dirs:
    if not os.path.exists(s_dir):
        print(f"Directory does not exist: {s_dir}")
        continue
    print(f"Scanning directory: {s_dir}")
    for root, dirs, files in os.walk(s_dir):
        # Skip node_modules or large unneeded files if any
        if "node_modules" in root or ".git" in root:
            continue
        for file in files:
            # Skip media and large binary files
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.zip', '.xlsx', '.pdf', '.exe', '.dll')):
                continue
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    for target in targets:
                        if target in content.lower():
                            # Find exact lines
                            f.seek(0)
                            lines = f.readlines()
                            for i, line in enumerate(lines):
                                if target in line.lower():
                                    print(f"MATCH in {filepath} | Line {i+1} (Target: {target}):")
                                    print(f"  {line.strip()[:200]}")
                                    found_count += 1
            except Exception as e:
                pass

print(f"\nScan completed. Total matches found: {found_count}")
