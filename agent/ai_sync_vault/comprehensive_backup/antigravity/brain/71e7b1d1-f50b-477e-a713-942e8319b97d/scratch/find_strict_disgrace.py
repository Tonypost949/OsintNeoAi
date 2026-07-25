import os

matches_file = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\tablet_matches_utf8.txt"

exact_terms = ["disgrace", "dsigrace", "national disgrace"]

print("Filtering for exact terms...")

found_files = {}

with open(matches_file, 'r', encoding='utf-8') as f:
    for line in f:
        # Ignore our scripts
        if any(x in line for x in ["search_tablet_download_content.py", "search_results_utf8.txt", "disgrace_filtered_results.txt", "tablet_matches_utf8.txt"]):
            continue
        line_lower = line.lower()
        for term in exact_terms:
            if term in line_lower:
                # Parse the path and line number
                # format: [path:Lnum] text
                if line.startswith('['):
                    end_idx = line.find(']')
                    if end_idx != -1:
                        path_part = line[1:end_idx]
                        text_part = line[end_idx+1:].strip()
                        if path_part not in found_files:
                            found_files[path_part] = []
                        found_files[path_part].append(text_part)

for filepath, occurrences in found_files.items():
    print(f"\n=========================================")
    print(f"FILE: {filepath}")
    print(f"Found {len(occurrences)} occurrences:")
    for occ in occurrences[:15]:
        print(f"  -> {occ[:200]}")
