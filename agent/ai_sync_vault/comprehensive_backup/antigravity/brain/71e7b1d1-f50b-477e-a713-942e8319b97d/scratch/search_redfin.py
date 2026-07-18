import os

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"
txt_files = [f for f in os.listdir(scratch_dir) if f.endswith(".txt") or f.endswith(".csv") or f.endswith(".html")]

print("--- Searching for Redfin URLs in scratch files ---")
for f in txt_files:
    path = os.path.join(scratch_dir, f)
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as file:
            for i, line in enumerate(file, 1):
                if "redfin.com" in line:
                    print(f"{f} Line {i}: {line.strip()[:150]}")
    except Exception as e:
        pass
