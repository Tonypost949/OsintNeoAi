import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"

keywords = ["self-dealing", "buntich", "pavalko", "shopoff", "mercy house", "conflict of interest"]

print("--- Searching scratch files for self-dealing or board conflict keywords ---")
for f in os.listdir(scratch_dir):
    path = os.path.join(scratch_dir, f)
    if os.path.isdir(path) or not (f.endswith(".txt") or f.endswith(".md") or f.endswith(".csv") or f.endswith(".html")):
        continue
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as file:
            for i, line in enumerate(file, 1):
                line_lower = line.lower()
                if any(kw in line_lower for kw in keywords):
                    print(f"File: {f}, Line {i}: {line.strip()[:180]}")
    except Exception as e:
        pass
print("Search complete.")
