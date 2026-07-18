import os

results_file = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\search_results_utf8.txt"
output_file = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\disgrace_filtered_results.txt"

terms = ["disgrace", "dsigrace", "national disgrace", "disg", "dsig"]

print(f"Reading {results_file}...")
matches = []
if os.path.exists(results_file):
    with open(results_file, 'r', encoding='utf-8', errors='ignore') as f:
        for line_num, line in enumerate(f, 1):
            line_lower = line.lower()
            for t in terms:
                if t in line_lower:
                    matches.append((line_num, line.strip()))
                    break

print(f"Found {len(matches)} matching lines.")
with open(output_file, 'w', encoding='utf-8') as out:
    for num, match in matches:
        out.write(f"Line {num}: {match}\n")

print("Saved matches to:", output_file)
for num, match in matches[:50]:
    print(f"[{num}] {match[:150]}")
