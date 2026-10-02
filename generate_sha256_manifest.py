import hashlib
import json
import os
import subprocess
import datetime

locker_root = r"C:\EVIDENCE_LOCKER_MASTER"
manifest_path = r"C:\EVIDENCE_LOCKER_MASTER\00_INDEX\EVIDENCE_LOCKER_SHA256_MANIFEST.json"

print(f"Generating Master SHA256 Evidence Manifest for {locker_root}...")

manifest = {
    "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "root_directory": locker_root,
    "files": {}
}

file_count = 0
for root, dirs, files in os.walk(locker_root):
    for name in files:
        if name == "EVIDENCE_LOCKER_SHA256_MANIFEST.json":
            continue
        rel_path = os.path.relpath(os.path.join(root, name), locker_root)
        full_path = os.path.join(root, name)
        
        hasher = hashlib.sha256()
        try:
            with open(full_path, "rb") as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
            
            manifest["files"][rel_path] = {
                "sha256": hasher.hexdigest(),
                "size_bytes": os.path.getsize(full_path)
            }
            file_count += 1
        except Exception as e:
            print(f"Error hashing {rel_path}: {e}")

manifest["total_files_hashed"] = file_count

with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

print(f"Manifest created successfully with {file_count} files hashed at {manifest_path}")

# Sync manifest to Google Drive
subprocess.run(["rclone", "copy", manifest_path, "gdrive:Sharedall/EVIDENCE_LOCKER_MASTER/00_INDEX", "-v"])
print("Synced manifest to gdrive:Sharedall/EVIDENCE_LOCKER_MASTER/00_INDEX")
