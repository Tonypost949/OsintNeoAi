import os

keywords = ["philippine", "offshore", "remittance", "wire", "remit", "international", "manila", "nunez", "barnes"]
search_dirs = [
    r"C:\Users\HP\OneDrive\Documents\opencode_work",
    r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"
]

print("Searching for remittance and offshore references...")
matches = []

for s_dir in search_dirs:
    if not os.path.exists(s_dir):
        continue
    for root, dirs, files in os.walk(s_dir):
        for f in files:
            if f.endswith((".py", ".md", ".csv", ".txt", ".sql")):
                f_path = os.path.join(root, f)
                try:
                    with open(f_path, "r", encoding="utf-8", errors="ignore") as file_obj:
                        content = file_obj.read()
                        found = []
                        for kw in keywords:
                            if kw in content.lower():
                                found.append(kw)
                        if found:
                            matches.append((f_path, found))
                except Exception as e:
                    pass

print(f"Found {len(matches)} files with references:")
for path, kws in sorted(matches, key=lambda x: len(x[1]), reverse=True)[:30]:
    print(f" - {os.path.basename(path)}: {kws} ({path})")
