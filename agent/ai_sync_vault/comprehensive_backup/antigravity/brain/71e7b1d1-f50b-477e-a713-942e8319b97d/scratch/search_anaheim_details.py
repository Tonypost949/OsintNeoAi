import os
import sys

# Configure standard output to use UTF-8
sys.stdout.reconfigure(encoding='utf-8')

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"
path = os.path.join(scratch_dir, "anaheim_details.txt")

print("--- Searching anaheim_details.txt for Covenant, 632, East ---")
if os.path.exists(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(term in line_lower for term in ["covenant", "632", "east st"]):
                print(f"\nMatch at line {i+1}:")
                # print context
                start = max(0, i-5)
                end = min(len(lines), i+6)
                for j in range(start, end):
                    marker = ">>>" if j == i else "   "
                    print(f"{marker} {j+1}: {lines[j].strip()}")
                print("-" * 40)
else:
    print("File not found.")
