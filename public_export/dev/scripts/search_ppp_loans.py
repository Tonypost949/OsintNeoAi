import os
import json
import re
from pathlib import Path

root = Path(r'C:\OsintNeoAi')
target_terms = ['ppp', 'paycheck protection', 'sba', 'eidl', 'forgiveness', 'ppp loan', 'ppp nationwide', 'fraud ring cluster', 'sole proprietorship']

print("=== SEARCHING REPOSITORY FOR PPP LOANS & SBA FRAUD SWEEP EVIDENCE ===")
matches = []

for f in root.glob('**/*.*'):
    if f.is_file() and f.suffix in ['.json', '.txt', '.csv', '.md']:
        path_str = str(f)
        if 'opencode_work' in path_str or '.git' in path_str or 'copilot-worktrees' in path_str:
            continue
        try:
            content = f.read_text(encoding='utf-8', errors='ignore')
            content_lower = content.lower()
            if 'ppp' in content_lower or 'sba' in content_lower or 'paycheck' in content_lower:
                for line in content.splitlines():
                    line_lower = line.lower()
                    if any(t in line_lower for t in target_terms):
                        matches.append({
                            'source': f.name,
                            'path': str(f),
                            'snippet': line.strip()[:200]
                        })
                        if len(matches) >= 50:
                            break
        except Exception:
            pass

out_file = root / 'data' / 'ppp_loans_search.json'
out_file.write_text(json.dumps(matches, indent=2), encoding='utf-8')

print(f"✓ Total PPP Loan & SBA Sweep Matches Found: {len(matches)}")
print(f"✓ Saved search results to: {out_file}\n")

print("Top PPP Loan Matches:")
for m in matches[:20]:
    print(f"[{m['source']}]: {m['snippet'][:120]}")
