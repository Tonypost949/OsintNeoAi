import os

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"

def search_exact(filename):
    filepath = os.path.join(scratch_dir, filename)
    if not os.path.exists(filepath):
        print(f"{filename} does not exist!")
        return
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    lines = content.splitlines()
    print(f"\n==================================================")
    print(f"EXACT SEARCH IN: {filename}")
    print(f"==================================================")
    
    targets = ["213 n. gilbert", "213 gilbert", "632 n. east", "632 east", "covenant house"]
    
    found = 0
    for idx, line in enumerate(lines):
        line_lower = line.lower()
        if any(t in line_lower for t in targets):
            # Print the line and 3 lines of context around it
            print(f"\n[Line {idx+1} Match]:")
            start = max(0, idx - 3)
            end = min(len(lines), idx + 4)
            for j in range(start, end):
                prefix = "  >>> " if j == idx else "      "
                print(f"{prefix}{lines[j]}")
            found += 1
            if found >= 30:
                print("... Truncated after 30 matches ...")
                break
    print(f"Total specific matches found: {found}")

search_exact("anaheim_details.txt")
search_exact("anaheim_gilbert_east_covenant_matches.txt")
