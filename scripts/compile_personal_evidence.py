import json
import re
from pathlib import Path

root = Path(r'C:\OsintNeoAi')
targets = ['feinstein', 'edd', 'sba', 'dfeh', 't-mobile', 'tmobile', 'cftc', 'aig', 'identity theft', 'id theft', 'police report']

matches = []
files = list(root.glob('evidence/**/*.*')) + list(root.glob('docs/**/*.*')) + list(root.glob('master_osint_sheet/*.csv'))

for f in files:
    if f.is_file() and f.suffix in ['.txt', '.csv', '.json', '.md']:
        path_str = str(f)
        if 'opencode_work' in path_str or 'copilot-worktrees' in path_str or 'archive' in path_str:
            continue
        try:
            content = f.read_text(encoding='utf-8', errors='ignore')
            for line in content.splitlines():
                line_lower = line.lower()
                for t in targets:
                    if t in line_lower:
                        matches.append({
                            'file': f.name,
                            'path': str(f),
                            'keyword': t,
                            'snippet': line.strip()[:200]
                        })
                        break
        except Exception:
            pass

out_file = root / 'data' / 'personal_timeline_evidence.json'
out_file.write_text(json.dumps(matches, indent=2), encoding='utf-8')
print(f"PERSONAL EVIDENCE MATCHES EXTRACTED & SAVED: {len(matches)} matches written to {out_file}")
