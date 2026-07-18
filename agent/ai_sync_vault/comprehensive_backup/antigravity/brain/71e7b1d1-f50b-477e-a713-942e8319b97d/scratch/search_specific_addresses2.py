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
    print(f"EXHAUSTIVE SEARCH IN: {filename}")
    print(f"==================================================")
    
    targets = ["gilbert", "east st", "east street", "632 n. east", "213 n. gilbert", "covenant"]
    
    for idx, line in enumerate(lines):
        line_lower = line.lower()
        if any(t in line_lower for t in targets):
            # Print the line
            print(f"L{idx+1}: {line}")

search_exact("anaheim_gilbert_east_covenant_matches.txt")
