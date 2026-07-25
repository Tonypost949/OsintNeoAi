import os
import re

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"

html_files = [f for f in os.listdir(scratch_dir) if f.endswith('.html')]

print(f"Scanning {len(html_files)} HTML files for 'disgrace' / 'national' / 'dsig' / 'disg' / 'dsigrace' / 'national disgrace'...")

keywords = [r"disgrace", r"dsigrace", r"disgr", r"dsig", r"disg"]

for hf in html_files:
    path = os.path.join(scratch_dir, hf)
    print(f"Scanning {hf}...")
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            # Let's search for disgraced or disgrace or disg
            for kw in keywords:
                matches = list(re.finditer(kw, content, re.IGNORECASE))
                if matches:
                    print(f"  -> Found {len(matches)} matches for '{kw}' in {hf}!")
                    # Print context around first few matches
                    for m in matches[:5]:
                        start = max(0, m.start() - 100)
                        end = min(len(content), m.end() + 100)
                        print(f"     Match context: ... {content[start:end].strip().replace(chr(10), ' ')} ...")
    except Exception as e:
        print(f"Error reading {hf}: {e}")
