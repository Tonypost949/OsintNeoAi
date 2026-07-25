"""Sync ALL projects to Google Drive sharedall folder"""
import os, shutil, time
from datetime import datetime

DEST = r"G:\osint-agent\sharedall"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")

# What to copy: (source, dest_subfolder_name)
SOURCES = [
    (r"C:\Users\HP\OneDrive\Documents\opencode_work", "opencode_work"),
    (r"C:\Users\HP\.gemini\antigravity-ide\scratch", "antigravity_projects"),
    (r"C:\Users\HP\.local\share\opencode", "opencode_local_data"),
]

os.makedirs(DEST, exist_ok=True)

stats = {"copied": 0, "skipped": 0, "errors": 0, "bytes": 0}
manifest_lines = []

for src_root, subfolder in SOURCES:
    if not os.path.isdir(src_root):
        print(f"[SKIP] Not found: {src_root}")
        continue
    
    dest_root = os.path.join(DEST, subfolder)
    
    for root, dirs, files in os.walk(src_root):
        # Skip __pycache__, .git, node_modules, venv
        dirs[:] = [d for d in dirs if d not in ('__pycache__', '.git', 'node_modules', 'venv', 'env', '.venv')]
        
        for fname in files:
            src = os.path.join(root, fname)
            rel = os.path.relpath(src, src_root)
            dst = os.path.join(dest_root, rel)
            
            try:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                sz = os.path.getsize(src)
                
                # Skip if identical
                if os.path.exists(dst) and os.path.getsize(dst) == sz:
                    stats["skipped"] += 1
                    continue
                
                shutil.copy2(src, dst)
                stats["copied"] += 1
                stats["bytes"] += sz
                manifest_lines.append(f"{rel}  ({sz/1024:.0f} KB)")
                
                if stats["copied"] % 200 == 0:
                    mb = stats["bytes"] / 1e6
                    print(f"  {stats['copied']} files, {mb:.0f} MB copied...")
                    
            except Exception as e:
                stats["errors"] += 1
                print(f"  [ERR] {rel}: {e}")

# Write manifest
manifest_path = os.path.join(DEST, f"sync_manifest_{TS}.txt")
with open(manifest_path, "w") as f:
    f.write(f"Sync completed: {datetime.now().isoformat()}\n")
    f.write(f"Sources:\n")
    for s, sub in SOURCES:
        f.write(f"  {s} -> {sub}\n")
    f.write(f"\nStats: {stats['copied']} copied, {stats['skipped']} skipped, {stats['errors']} errors\n")
    f.write(f"Total: {stats['bytes']/1e6:.1f} MB copied\n\n")
    f.write("Files:\n")
    f.write("\n".join(manifest_lines))

print(f"\n=== SYNC COMPLETE ===")
print(f"  Copied:  {stats['copied']}")
print(f"  Skipped: {stats['skipped']}")
print(f"  Errors:  {stats['errors']}")
print(f"  Total:   {stats['bytes']/1e6:.1f} MB")
print(f"  Destination: {DEST}")
