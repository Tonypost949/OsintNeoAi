import os

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"
files = ["anaheim_details.txt", "anaheim_gilbert_east_covenant_matches.txt"]

for f in files:
    path = os.path.join(scratch_dir, f)
    if os.path.exists(path):
        print(f"\nSearching {f}...")
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as file:
                lines = file.readlines()
                for i, line in enumerate(lines):
                    line_lower = line.lower()
                    if "covenant" in line_lower or "632" in line_lower or "east st" in line_lower or "east street" in line_lower:
                        print(f"  Line {i+1}: {line.strip()[:150]}")
        except Exception as e:
            print(f"  Error reading {f}: {e}")
