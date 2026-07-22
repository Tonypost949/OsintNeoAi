import os
import shutil

src_dir = r"C:\Users\HP\Downloads"
dest_dir = r"C:\Users\HP\OneDrive\Documents\opencode_work\Private_EDR_2025_Real"

if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)
    print(f"Created destination directory: {dest_dir}")

copied_files = []
for root, dirs, files in os.walk(src_dir):
    for f in files:
        if '7969270' in f:
            src_path = os.path.join(root, f)
            dest_path = os.path.join(dest_dir, f)
            
            # Avoid overwriting with identical file, but copy if new or name unique
            shutil.copy2(src_path, dest_path)
            copied_files.append(f)

print(f"Successfully copied {len(copied_files)} files to {dest_dir}:")
for f in sorted(list(set(copied_files))):
    print(f" - {f}")
