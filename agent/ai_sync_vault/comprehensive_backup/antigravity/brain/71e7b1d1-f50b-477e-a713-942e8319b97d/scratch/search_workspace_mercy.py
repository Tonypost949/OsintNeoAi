import os

workspace_root = r"c:\Users\HP\OneDrive\Documents\AG2OSINTNEOMAXX"

print(f"--- Searching workspace root: {workspace_root} for Mercy House or Conflicts ---")
matches = []
for root, dirs, files in os.walk(workspace_root):
    for f in files:
        f_lower = f.lower()
        if "mercy" in f_lower or "conflict" in f_lower or "buntich" in f_lower or "paval" in f_lower or "shopoff" in f_lower or "meli" in f_lower:
            full_path = os.path.join(root, f)
            print(f"Match: {f} -> {full_path}")
            matches.append(full_path)

if len(matches) == 0:
    print("No matching files found.")
