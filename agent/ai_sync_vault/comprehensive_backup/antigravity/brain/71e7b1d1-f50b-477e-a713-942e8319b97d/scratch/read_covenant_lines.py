import os
import sys

# Configure standard output to use UTF-8
sys.stdout.reconfigure(encoding='utf-8')

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"
path = os.path.join(scratch_dir, "anaheim_gilbert_east_covenant_matches.txt")

print("--- Printing lines 1870 to 2010 from anaheim_gilbert_east_covenant_matches.txt ---")
if os.path.exists(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
        start = 1869
        end = min(2020, len(lines))
        for idx in range(start, end):
            print(f"{idx+1}: {lines[idx].strip()}")
else:
    print("File not found.")
