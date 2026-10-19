import os

start_dir = r"C:\Users\HP\OneDrive\Documents\opencode_work_backup\OPENCODE_CONFIG_20260702"
print(f"[*] Scanning backup folder recursively: {start_dir}")

all_files = []
for root, dirs, files in os.walk(start_dir):
    # Skip node_modules to avoid cluttering output
    if "node_modules" in dirs:
        dirs.remove("node_modules")
    for file in files:
        full_path = os.path.join(root, file)
        rel_path = os.path.relpath(full_path, start_dir)
        all_files.append((rel_path, os.path.getsize(full_path)))

print(f"[+] Total files found (excluding node_modules): {len(all_files)}")
print("\nTop 50 files by size:")
all_files.sort(key=lambda x: x[1], reverse=True)
for rel, size in all_files[:50]:
    print(f"  {size:>10} bytes  {rel}")
