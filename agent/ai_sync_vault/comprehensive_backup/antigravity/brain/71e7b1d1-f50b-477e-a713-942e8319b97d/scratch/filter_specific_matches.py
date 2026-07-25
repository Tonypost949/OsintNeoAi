import os

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"
txt_path = os.path.join(scratch_dir, "deepseek_investigation_matches_formatted.txt")
out_path = os.path.join(scratch_dir, "anaheim_gilbert_east_covenant_matches.txt")

if not os.path.exists(txt_path):
    print("Formatted matches text file does not exist!")
    os._exit(1)

with open(txt_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

specific_keywords = ["gilbert", "east st", "covenant"]

matching_indices = []
for i, line in enumerate(lines):
    for kw in specific_keywords:
        if kw in line.lower():
            matching_indices.append((i, kw))

# Let's save a file containing matching locations and a window of 30 lines before and 30 lines after each occurrence.
with open(out_path, 'w', encoding='utf-8') as out_f:
    out_f.write(f"Matches for {specific_keywords} with surrounding context\n")
    out_f.write(f"=========================================================\n\n")
    
    for idx, kw in matching_indices:
        out_f.write(f"========================================================================\n")
        out_f.write(f"LINE {idx+1} | KEYWORD MATCH: {kw}\n")
        out_f.write(f"========================================================================\n")
        
        start = max(0, idx - 15)
        end = min(len(lines), idx + 25)
        for j in range(start, end):
            prefix = ">>> " if j == idx else "    "
            out_f.write(f"{prefix}{j+1}: {lines[j]}")
        out_f.write("\n\n")

print(f"Saved {len(matching_indices)} matches to {out_path}.")
