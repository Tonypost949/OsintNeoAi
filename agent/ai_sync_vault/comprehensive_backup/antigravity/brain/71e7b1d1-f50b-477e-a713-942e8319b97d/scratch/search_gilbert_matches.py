import os

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"
files = [
    "extracted_text_index_filtered.txt",
    "gilbert_matches_context.txt",
    "anaheim_gilbert_east_covenant_matches.txt",
    "anaheim_details.txt"
]

search_terms = ["213 n. gilbert", "213 n gilbert", "213 gilbert", "685,000", "685000"]
output_path = os.path.join(scratch_dir, "gilbert_specific_matches.txt")

with open(output_path, "w", encoding="utf-8") as out:
    out.write("Gilbert and 213 Specific Matches\n")
    out.write("================================\n\n")
    
    for filename in files:
        filepath = os.path.join(scratch_dir, filename)
        if not os.path.exists(filepath):
            out.write(f"File not found: {filename}\n")
            continue
            
        out.write(f"Searching {filename}...\n")
        match_count = 0
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                for i, line in enumerate(f, 1):
                    line_lower = line.lower()
                    if any(term in line_lower for term in search_terms):
                        out.write(f"Line {i}: {line.strip()[:200]}\n")
                        match_count += 1
                        if match_count > 100:
                            out.write("... truncated (too many matches) ...\n")
                            break
            out.write(f"Finished {filename}. Found {match_count} matches.\n\n")
        except Exception as e:
            out.write(f"Error reading {filename}: {str(e)}\n\n")

print("Done! Specific matches written to gilbert_specific_matches.txt")
