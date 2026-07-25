import os

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"
target_terms = ["dsig", "disg", "disgrace", "disgr", "national"]

print("Starting ultra-targeted fast scan of scratch folder files...")

matches = []

# List files directly under scratch folder
for f in os.listdir(scratch_dir):
    fp = os.path.join(scratch_dir, f)
    if os.path.isdir(fp):
        continue
    # Skip huge index or dataset files
    if os.path.getsize(fp) > 1000000:
        continue
    if f.endswith(('.txt', '.md', '.csv', '.json', '.html', '.py', '.xml', '.log')):
        try:
            with open(fp, 'r', encoding='utf-8', errors='ignore') as file_obj:
                for line_num, line in enumerate(file_obj, 1):
                    line_lower = line.lower()
                    for term in target_terms:
                        if term in line_lower:
                            matches.append(f"MATCH in {f} (Line {line_num}): {line.strip()[:200]}")
        except Exception as e:
            pass

print("\n--- ULTRA-TARGETED SEARCH RESULTS ---")
if matches:
    print(f"Found {len(matches)} occurrences:")
    for m in matches[:100]:
        print(m)
else:
    print("No occurrences found in scratch folder.")
