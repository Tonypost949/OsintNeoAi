import os
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

unzip_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\extracted\APT2024filesfull (Unzipped Files)"

print(f"Auditing extracted files in: {unzip_dir}")

ext_counts = {}
dir_counts = {}
total_files = 0

for root, dirs, files in os.walk(unzip_dir):
    for f in files:
        total_files += 1
        fp = os.path.join(root, f)
        ext = os.path.splitext(f)[1].lower()
        ext_counts[ext] = ext_counts.get(ext, 0) + 1
        
        rel_dir = os.path.relpath(root, unzip_dir)
        dir_counts[rel_dir] = dir_counts.get(rel_dir, 0) + 1

print(f"\nTotal files found: {total_files}")
print("\nFiles by directory:")
for d, count in sorted(dir_counts.items()):
    print(f"  - {d}: {count} files")

print("\nFiles by extension:")
for ext, count in sorted(ext_counts.items()):
    print(f"  - '{ext}': {count} files")
