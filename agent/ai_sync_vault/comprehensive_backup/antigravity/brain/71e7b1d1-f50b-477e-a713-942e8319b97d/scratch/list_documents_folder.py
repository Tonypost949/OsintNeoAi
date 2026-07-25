import os

paths = [
    r"C:\Users\HP\OneDrive\Documents",
    r"C:\Users\HP\Documents"
]

for p in paths:
    print(f"\nChecking directory: {p}")
    if os.path.exists(p):
        try:
            items = os.listdir(p)
            print(f"Total items found: {len(items)}")
            zip_files = [i for i in items if i.lower().endswith('.zip')]
            print(f"ZIP files found ({len(zip_files)}):")
            for zf in zip_files:
                full_p = os.path.join(p, zf)
                size_gb = os.path.getsize(full_p) / (1024**3)
                print(f"  - {zf} | Size: {size_gb:.3f} GB ({os.path.getsize(full_p)} bytes)")
        except Exception as e:
            print(f"  Error listing directory: {e}")
    else:
        print("  Directory does not exist.")
