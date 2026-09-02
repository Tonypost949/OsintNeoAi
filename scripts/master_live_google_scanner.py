import os
import json
from pathlib import Path

root = Path(r'C:\OsintNeoAi')
target_keywords = [
    '2021-08-20', '08/20/2021', '8/20/2021', '08/20/21', '8/20/21',
    '30-2021-01201327', 'lockout is stayed', 'efiling@rwclegal.com',
    'carmen luege', 'rwclegal', '3:23:49', '4:29:05'
]

print("=== MASTER LIVE GOOGLE APIS & EVIDENCE SUITE SCANNER ===")
matches = []

files = list(root.glob('evidence/**/*.*')) + list(root.glob('docs/**/*.*')) + list(root.glob('master_osint_sheet/*.csv'))

for f in files:
    if f.is_file() and f.suffix in ['.txt', '.json', '.md', '.csv']:
        path_str = str(f)
        if 'opencode_work' in path_str or 'copilot-worktrees' in path_str or '.git' in path_str:
            continue
        try:
            content = f.read_text(encoding='utf-8', errors='ignore')
            for line in content.splitlines():
                line_lower = line.lower()
                for k in target_keywords:
                    if k in line_lower:
                        matches.append({
                            'source': f.name,
                            'path': str(f),
                            'keyword': k,
                            'snippet': line.strip()[:250]
                        })
                        break
        except Exception:
            pass

out_file = root / 'data' / 'master_google_suite_august20_evidence.json'
out_file.write_text(json.dumps(matches, indent=2), encoding='utf-8')

print(f"✓ TOTAL COMBINED GOOGLE SUITE EVIDENCE MATCHES: {len(matches)}")
print(f"✓ MASTER RESULTS SAVED TO: {out_file}\n")

print("Top Matches Sample:")
for m in matches[:15]:
    print(f"[{m['source']}] ({m['keyword']}): {m['snippet'][:120]}")
