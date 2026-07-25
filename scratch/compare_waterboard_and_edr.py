import os

public_dir = r"c:\Users\HP\OneDrive\Documents\OsintNeoAi\opencode_work\Official_GeoTracker_T10000018579"
private_dir = r"c:\Users\HP\OneDrive\Documents\OsintNeoAi\opencode_work\Private_EDR_2025_Real"

print("=== PUBLIC GEOTRACKER FILES (WATERBOARD) ===")
if os.path.exists(public_dir):
    for f in sorted(os.listdir(public_dir)):
        p = os.path.join(public_dir, f)
        if os.path.isfile(p):
            sz = os.path.getsize(p) / 1e6
            print(f"  [FILE] {f} ({sz:.2f} MB)")
else:
    print("Public directory not found")

print("\n=== PRIVATE REAL EDR FILES (2025 UNPUBLISHED) ===")
if os.path.exists(private_dir):
    files = sorted(os.listdir(private_dir))
    print(f"Found {len(files)} private EDR files.")
    for f in files[:20]: # Print first 20 for brief summary
        p = os.path.join(private_dir, f)
        if os.path.isfile(p):
            sz = os.path.getsize(p) / 1e6
            print(f"  [FILE] {f} ({sz:.2f} MB)")
    if len(files) > 20:
        print(f"  ... and {len(files) - 20} more files.")
else:
    print("Private directory not found")
