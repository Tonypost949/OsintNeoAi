import os

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"
txt_path = os.path.join(scratch_dir, "deepseek_investigation_matches_formatted.txt")

if not os.path.exists(txt_path):
    print("Formatted matches text file does not exist!")
    os._exit(1)

keywords = ["gilbert", "east st", "covenant", "nunez", "barnes"]

with open(txt_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

# Let's search for keywords and print matching blocks.
# A block in the text file starts with "----------------------------------------" or similar, 
# or we can just find lines matching the keywords and print 20 lines before and after.

matches_count = {kw: 0 for kw in keywords}
matching_blocks = []

current_header = ""
current_match_header = ""
current_block_lines = []

for i, line in enumerate(lines):
    # Detect conversation header
    if line.startswith("FOLDER ") or line.startswith("--------------------------------------------------------------------------------"):
        current_header = line.strip()
    elif line.startswith("Match #"):
        current_match_header = line.strip()
        
    for kw in keywords:
        if kw in line.lower():
            matches_count[kw] += 1
            # Add to matching blocks: line index, keyword, context
            matching_blocks.append((i, kw, current_header, current_match_header))

print("Keyword Occurrences:")
for kw, count in matches_count.items():
    print(f"  {kw}: {count}")

print("\nDetailing specific matches for gilbert, east st, covenant, nunez:")
for idx, kw, header, m_header in matching_blocks:
    if kw in ["gilbert", "east st", "covenant", "nunez"]:
        print(f"\n==================================================")
        print(f"Line {idx+1} | Keyword: {kw}")
        print(f"Context: {header} -> {m_header}")
        print(f"==================================================")
        # Print 5 lines before and 15 lines after
        start = max(0, idx - 5)
        end = min(len(lines), idx + 15)
        for j in range(start, end):
            prefix = ">>> " if j == idx else "    "
            line_to_print = lines[j].strip()
            # safely encode to ascii using backslashreplace to avoid crash on Windows stdout
            safe_line = line_to_print.encode('ascii', 'backslashreplace').decode('ascii')
            print(f"{prefix}{j+1}: {safe_line}")
