import os

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"
files_to_search = [
    "anaheim_gilbert_east_covenant_matches.txt",
    "filtered_gilbert_east.txt",
    "exact_address_matches.txt",
    "anaheim_details.txt"
]

search_terms = ["gilbert", "213", "east st", "covenant"]

for filename in files_to_search:
    filepath = os.path.join(scratch_dir, filename)
    if not os.path.exists(filepath):
        print(f"File not found: {filename}")
        continue
    
    print(f"\n--- Searching in {filename} ---")
    matches = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f, 1):
                line_lower = line.lower()
                if any(term in line_lower for term in search_terms):
                    matches.append((i, line.strip()))
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        continue
        
    print(f"Found {len(matches)} matches.")
    # Show first 30 matches
    for idx, match in matches[:30]:
        print(f"Line {idx}: {match[:200]}")
    if len(matches) > 30:
        print(f"... and {len(matches) - 30} more.")
