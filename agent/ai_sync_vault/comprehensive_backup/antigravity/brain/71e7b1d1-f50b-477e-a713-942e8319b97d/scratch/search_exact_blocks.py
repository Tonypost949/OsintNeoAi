import os

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"

def search_blocks(filename, keywords):
    filepath = os.path.join(scratch_dir, filename)
    if not os.path.exists(filepath):
        print(f"{filename} does not exist!")
        return
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    print(f"\n==================================================")
    print(f"BLOCK SEARCH IN: {filename}")
    print(f"==================================================")
    
    # Let's split by double newlines or common block headers if we can find them
    # For now, let's search for keywords and print 15 lines before and after
    lines = content.splitlines()
    for idx, line in enumerate(lines):
        line_lower = line.lower()
        if any(kw.lower() in line_lower for kw in keywords):
            print(f"\n--- Found '{line.strip()}' on Line {idx+1} ---")
            start = max(0, idx - 10)
            end = min(len(lines), idx + 15)
            for j in range(start, end):
                prefix = "  >>> " if j == idx else "      "
                print(f"{prefix}{lines[j]}")
            print("-" * 50)

search_blocks("exact_address_matches.txt", ["213", "gilbert", "632", "east"])
