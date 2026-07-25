import os
import hashlib

src_dir = r"C:\Users\HP\Downloads"

def get_md5(path):
    hash_md5 = hashlib.md5()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception:
        return None

file_map = {}
for root, dirs, files in os.walk(src_dir):
    for f in files:
        if '7969270' in f:
            path = os.path.join(root, f)
            size = os.path.getsize(path)
            md5 = get_md5(path)
            
            if f not in file_map:
                file_map[f] = []
            file_map[f].append({
                "path": path,
                "size": size,
                "md5": md5
            })

print("=== DUPLICATE FILENAME ANALYSIS ===")
has_issues = False
for fname, occurrences in file_map.items():
    if len(occurrences) > 1:
        # Check if sizes or hashes differ
        sizes = {occ["size"] for occ in occurrences}
        hashes = {occ["md5"] for occ in occurrences}
        
        if len(sizes) > 1 or len(hashes) > 1:
            has_issues = True
            print(f"\nConflict found for filename: {fname}")
            for occ in occurrences:
                print(f"  - Size: {occ['size']} bytes, MD5: {occ['md5']}, Path: {occ['path']}")
        else:
            print(f"Filename {fname}: {len(occurrences)} occurrences are identical (Size: {occurrences[0]['size']} bytes, MD5: {occurrences[0]['md5']})")

if not has_issues:
    print("\nAll files with duplicate names are byte-for-byte identical. No content was lost during overwrite.")
