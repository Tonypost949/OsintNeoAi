import os

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"

def search_blocks(filename, keywords, output_filename):
    filepath = os.path.join(scratch_dir, filename)
    outpath = os.path.join(scratch_dir, output_filename)
    if not os.path.exists(filepath):
        print(f"{filename} does not exist!")
        return
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    lines = content.splitlines()
    output_lines = []
    output_lines.append(f"==================================================")
    output_lines.append(f"BLOCK SEARCH IN: {filename}")
    output_lines.append(f"==================================================")
    
    for idx, line in enumerate(lines):
        line_lower = line.lower()
        if any(kw.lower() in line_lower for kw in keywords):
            output_lines.append(f"\n--- Found '{line.strip()}' on Line {idx+1} ---")
            start = max(0, idx - 10)
            end = min(len(lines), idx + 20)
            for j in range(start, end):
                prefix = "  >>> " if j == idx else "      "
                output_lines.append(f"{prefix}{lines[j]}")
            output_lines.append("-" * 50)
            
    with open(outpath, 'w', encoding='utf-8') as f:
        f.write("\n".join(output_lines))
    print(f"Results written to {output_filename} successfully!")

search_blocks("exact_address_matches.txt", ["213", "gilbert", "632", "east"], "exact_block_matches_output.txt")
search_blocks("filtered_gilbert_east.txt", ["213", "gilbert", "632", "east"], "exact_block_matches_output2.txt")
