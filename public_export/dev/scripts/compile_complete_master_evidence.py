import json
import re
from pathlib import Path

root = Path(r'C:\OsintNeoAi')
keywords = [
    'feinstein', 'edd', 'sba', 'dfeh', 'extort', 'extortion', 't-mobile', 'tmobile', 
    'chase', 'cftc', 'aig', 'assurant', 'chris ryan', 'shea', 'angels', 'msttrading', 
    'police report', '585008hwv0hfv', '3:20-mj-05007', '212 southbrook', 'ann verma'
]

matches = []
files = list(root.glob('evidence/**/*.*')) + list(root.glob('docs/**/*.*')) + list(root.glob('master_osint_sheet/*.csv'))

for f in files:
    if f.is_file() and f.suffix in ['.txt', '.csv', '.json', '.md']:
        path_str = str(f)
        if 'opencode_work' in path_str or 'copilot-worktrees' in path_str or '.git' in path_str:
            continue
        try:
            content = f.read_text(encoding='utf-8', errors='ignore')
            for line in content.splitlines():
                line_lower = line.lower()
                for k in keywords:
                    if k in line_lower:
                        matches.append({
                            'file': f.name,
                            'path': str(f),
                            'keyword': k,
                            'snippet': line.strip()[:250]
                        })
                        break
        except Exception:
            pass

out_file = root / 'data' / 'complete_master_personal_evidence_index.json'
out_file.write_text(json.dumps(matches, indent=2), encoding='utf-8')

print(f"COMPLETE MASTER PERSONAL EVIDENCE INDEX CREATED: {len(matches)} matches written to {out_file}")
