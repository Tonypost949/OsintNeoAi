import json
import re
from pathlib import Path

root = Path(r'C:\OsintNeoAi')
targets = ['angels', 'shea', 'shea homes', 'chase', 'chase bank', 'id theft', 'identity theft', 'insurance']

matches = []
files = list(root.glob('**/*.txt')) + list(root.glob('**/*.json')) + list(root.glob('**/*.md')) + list(root.glob('**/*.csv')) + list(root.glob('**/*.html'))

for f in files:
    if f.is_file():
        path_str = str(f)
        if 'opencode_work' in path_str or 'copilot-worktrees' in path_str or '.git' in path_str:
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
                            'snippet': line.strip()[:250]
                        })
                        break
        except Exception:
            pass

out_file = root / 'data' / 'angels_shea_chase_idtheft_evidence.json'
out_file.write_text(json.dumps(matches, indent=2), encoding='utf-8')
print(f"TOTAL ANGELS / SHEA / CHASE / ID THEFT MATCHES FOUND: {len(matches)}")
print("\nSample matches:")
for m in matches[:25]:
    print(f"[{m['file']}] ({m['keyword']}): {m['snippet'][:120]}")
