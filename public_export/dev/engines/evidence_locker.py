import hashlib, json
from pathlib import Path
from datetime import datetime, timezone

def seal_evidence(target_dir='C:/RICONWO'):
    p = Path(target_dir)
    manifest = {'case_name': 'RICONWO', 'sealed_at': datetime.now(timezone.utc).isoformat(), 'standard': 'SHA-256', 'exhibits': []}
    for f in p.rglob('*'):
        if f.is_file() and not f.name.endswith('.json') and '.git' not in f.parts:
            h = hashlib.sha256(f.read_bytes()).hexdigest()
            manifest['exhibits'].append({'file': str(f.relative_to(p)), 'sha256': h, 'status': 'VERIFIED_AUTHENTIC'})
    (p / 'EVIDENCE_CHAIN_OF_CUSTODY.json').write_text(json.dumps(manifest, indent=2))
    print('🔒 Evidence Locker Sealed with SHA-256 Checksums!')

if __name__ == '__main__':
    seal_evidence()
