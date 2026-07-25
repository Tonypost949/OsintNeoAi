import os
import sys

# Configure standard output to use UTF-8
sys.stdout.reconfigure(encoding='utf-8')

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"
path = os.path.join(scratch_dir, "anaheim_details.txt")

print("--- Printing lines 930 to 1050 from anaheim_details.txt ---")
if os.path.exists(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
        start = 920
        end = min(1100, len(lines))
        for idx in range(start, end):
            print(f"{idx+1}: {lines[idx].strip()}")
else:
    print("File not found.")
