import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

base_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\extracted\APT2024filesfull (Unzipped Files)"

targets = [
    ("Australia", "澳大利亚"),
    ("Guinea", "几内亚"),
    ("Djibouti", "吉布提"),
    ("Cambodia", "柬埔寨"),
    ("Congo", "刚果"),
    ("North Macedonia", "北马其顿"),
    ("East Timor", "东帝汶"),
    ("Kazakhstan", "哈萨克斯坦"),
    ("Dalai", "达赖"),
    ("NATO", "北约"),
    ("Vietnam", "越南"),
    ("Myanmar", "缅甸")
]

print("Searching extracted files for target countries and organizations...")

results = {}

for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.lower().endswith(('.md', '.txt', '.log')):
            fp = os.path.join(root, file)
            try:
                with open(fp, 'r', encoding='utf-8', errors='ignore') as f_obj:
                    content = f_obj.read()
                    for eng, chi in targets:
                        matches = []
                        if eng.lower() in content.lower() or chi in content:
                            # Find matching lines with context
                            lines = content.splitlines()
                            for i, line in enumerate(lines):
                                if eng.lower() in line.lower() or chi in line:
                                    matches.append((i+1, line.strip()))
                            
                            key = f"{eng} / {chi}"
                            if key not in results:
                                results[key] = []
                            results[key].append((os.path.relpath(fp, base_dir), len(matches), matches[:3]))
            except Exception as e:
                pass

for target_key, files_found in sorted(results.items()):
    print(f"\n==================================================")
    print(f"Target: {target_key} | Found in {len(files_found)} files")
    print(f"==================================================")
    for rel_path, match_count, snippets in files_found[:10]:
        print(f"File: {rel_path} ({match_count} matches)")
        for line_num, text in snippets:
            print(f"  Line {line_num}: {text[:150]}")
        print("-" * 30)
