import os
import re

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"

files = ["untitled.html", "HTML download dl.html to"]

keywords = ["disgrace", "national", "dsigrace", "disg", "dsig"]

for f_name in files:
    path = os.path.join(scratch_dir, f_name)
    if os.path.exists(path):
        print(f"Reading {f_name} (Size: {os.path.getsize(path)} bytes)...")
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                print(f"File {f_name} read successfully. Character count: {len(content)}")
                for kw in keywords:
                    matches = list(re.finditer(kw, content, re.IGNORECASE))
                    if matches:
                        print(f"  -> Found {len(matches)} matches for '{kw}' in {f_name}!")
                        for m in matches[:5]:
                            start = max(0, m.start() - 150)
                            end = min(len(content), m.end() + 150)
                            print(f"     Match context: ... {content[start:end].strip().replace(chr(10), ' ')} ...")
        except Exception as e:
            print(f"Error reading {f_name}: {e}")
    else:
        print(f"File {f_name} does not exist at {path}.")
