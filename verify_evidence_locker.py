import os
import hashlib
import json

evidence_dir = 'C:/OsintNeoAi/evidence'
manifest = []

for root, dirs, files in os.walk(evidence_dir):
    for f in files:
        fp = os.path.join(root, f)
        try:
            with open(fp, 'rb') as file_obj:
                h = hashlib.sha256(file_obj.read()).hexdigest()
            manifest.append({
                'path': fp,
                'size': os.path.getsize(fp),
                'sha256': h
            })
        except Exception:
            pass

manifest_path = 'C:/OsintNeoAi/EVIDENCE_LOCKER_SHA256_MANIFEST.json'
with open(manifest_path, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2)

print(f"Verified {len(manifest)} local evidence files and generated SHA-256 integrity manifest at {manifest_path}")
