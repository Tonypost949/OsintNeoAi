import os

matches_file = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\tablet_matches_utf8.txt"

print(f"Filtering {matches_file}...")

with open(matches_file, 'r', encoding='utf-8') as f:
    for line in f:
        # Ignore our own scripts, result logs, and other non-tablet report files
        if any(x in line for x in ["search_tablet_download_content.py", "search_results_utf8.txt", "disgrace_filtered_results.txt", "tablet_matches_utf8.txt"]):
            continue
        # Also print anything with "disgrace" or "dsigrace"
        if "disgrace" in line.lower() or "dsig" in line.lower() or "disg" in line.lower():
            # Clean path for readability
            print(line.strip())
