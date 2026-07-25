import os

search_paths = [
    r"C:\Users\HP\Downloads",
    r"C:\Users\HP\OneDrive",
    r"C:\Users\HP\Documents",
    r"C:\Users\HP\Desktop",
    r"c:\Users\HP\OneDrive\Documents\AG2OSINTNEOMAXX"
]

keywords = ["master", "osint", "sheet", "rico", "beeline", "tele2", "isoon", "anxun", "audit", "lead", "tracker", "target", "evidence"]

print("Searching for relevant OSINT files...")
found_files = []

for base_path in search_paths:
    if not os.path.exists(base_path):
        continue
    print(f"Searching in {base_path}...")
    for root, dirs, files in os.walk(base_path):
        # Skip some standard directories to avoid endless loops
        if any(p in root for p in ["AppData", "Local Settings", "Node_modules", "node_modules", "temp", "tmp"]):
            continue
        for f in files:
            f_lower = f.lower()
            matched = [kw for kw in keywords if kw in f_lower]
            if matched:
                fp = os.path.join(root, f)
                try:
                    size = os.path.getsize(fp)
                    found_files.append((fp, size, matched))
                except Exception:
                    pass

print(f"\nFound {len(found_files)} files with matching names:")
for fp, size, matched in sorted(found_files, key=lambda x: x[1] if x[1] else 0, reverse=True)[:100]:
    print(f"- {fp} ({size} bytes) matches {matched}")
