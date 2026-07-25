import os

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"
files_to_search = [
    "gilbert_specific_matches.txt",
    "filtered_gilbert_east.txt",
    "anaheim_gilbert_east_covenant_matches.txt",
    "anaheim_details.txt",
    "gilbert_safe_results.txt"
]

keywords = ["213", "632", "gilbert", "covenant", "east st"]

print("Starting deep context search across local files...")

for filename in files_to_search:
    filepath = os.path.join(scratch_dir, filename)
    if not os.path.exists(filepath):
        continue
        
    print(f"\n==================================================")
    print(f"FILE: {filename}")
    print(f"==================================================")
    
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
        
    match_count = 0
    for idx, line in enumerate(lines):
        line_lower = line.lower()
        # Look for combinations of keywords, e.g. "213" and "gilbert" or "632" and "east" or "covenant"
        if ("213" in line_lower and "gilbert" in line_lower) or ("632" in line_lower and "east" in line_lower) or ("covenant" in line_lower and "east" in line_lower) or ("covenant" in line_lower and "gilbert" in line_lower):
            match_count += 1
            print(f"--- Match #{match_count} at line {idx+1} ---")
            # Print a window of lines around the match
            start = max(0, idx - 8)
            end = min(len(lines), idx + 8)
            for j in range(start, end):
                prefix = ">> " if j == idx else "   "
                print(f"{prefix}{j+1}: {lines[j].strip()}")
            print("-" * 50)
            if match_count >= 15:
                print("Truncating further matches for this file...")
                break
