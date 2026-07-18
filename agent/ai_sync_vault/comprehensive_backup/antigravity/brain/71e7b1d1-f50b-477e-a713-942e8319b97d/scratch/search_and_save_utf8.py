import os

search_paths = [
    r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d",
    r"C:\Users\HP\OneDrive\Documents\AG2OSINTNEOMAXX",
    r"C:\OSINTNEOAIXL",
    r"C:\OSINT_HB_Data",
    r"C:\OSINT_Investigation_Anthony",
    r"C:\maltego_osint",
    r"C:\Users\HP\OneDrive\Documents"
]

target_terms = ["dsig", "disg", "disgrace", "disgr", "national"]
output_file = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\search_results_utf8.txt"

print("Starting safe robust search...")
matches = []

for base in search_paths:
    if not os.path.exists(base):
        continue
    print(f"Scanning path: {base}")
    for root, dirs, files in os.walk(base):
        # Skip system and noise folders
        if any(p in root for p in ["AppData", "node_modules", ".git", "temp", "tmp", "AomeiRecovery", ".system_generated"]):
            continue
        for f in files:
            # Skip massive files
            fp = os.path.join(root, f)
            try:
                sz = os.path.getsize(fp)
                if sz > 2000000: # 2MB limit
                    continue
                if f.endswith(('.txt', '.md', '.csv', '.json', '.html', '.py', '.xml', '.log')):
                    with open(fp, 'r', encoding='utf-8', errors='ignore') as file_obj:
                        for line_num, line in enumerate(file_obj, 1):
                            line_lower = line.lower()
                            for term in target_terms:
                                if term in line_lower:
                                    matches.append(f"MATCH in {fp} (Line {line_num}): {line.strip()}")
                                    break
            except Exception as e:
                pass

# Save results with utf-8 encoding to avoid Windows console errors
with open(output_file, 'w', encoding='utf-8') as out_f:
    out_f.write(f"Found {len(matches)} occurrences:\n\n")
    for m in matches:
        out_f.write(m + "\n")

print(f"Done! Saved {len(matches)} results to {output_file}")
