import os

workspace_dir = r"C:\Users\HP\OneDrive\Documents\AG2OSINTNEOMAXX"
target_terms = ["dsig", "disg", "disgrace", "disgr", "national"]

print("Running unrestricted workspace search for 'national' and 'dsig/disg' terms...")

matches = []

for root, dirs, files in os.walk(workspace_dir):
    if any(p in root for p in [".git", "node_modules"]):
        continue
    for f in files:
        fp = os.path.join(root, f)
        # Check all files, regardless of extension, up to 5MB in size
        try:
            if os.path.getsize(fp) > 5000000:
                continue
            with open(fp, 'r', encoding='utf-8', errors='ignore') as file_obj:
                for line_num, line in enumerate(file_obj, 1):
                    line_lower = line.lower()
                    for term in target_terms:
                        if term in line_lower:
                            matches.append(f"MATCH in {os.path.relpath(fp, workspace_dir)} (Line {line_num}): {line.strip()[:200]}")
        except Exception as e:
            pass

print("\n--- UNRESTRICTED WORKSPACE SEARCH RESULTS ---")
if matches:
    print(f"Found {len(matches)} occurrences:")
    for m in matches[:150]:
        print(m)
else:
    print("No occurrences found in workspace.")
