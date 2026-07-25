import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"
path = os.path.join(scratch_dir, "ingestion_plan_text.txt")

print("--- Printing lines 1680 to 1800 from ingestion_plan_text.txt ---")
if os.path.exists(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
        start = 1675
        end = min(1810, len(lines))
        for idx in range(start, end):
            print(f"{idx+1}: {lines[idx].strip()}")
else:
    print("File not found.")
