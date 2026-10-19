import os
import json
import re
from pathlib import Path

root = Path(r'C:\OsintNeoAi')
target_keywords = ['nichols', 'interior runoff', 'runoff', 'drain', 'discharge', 'industrial runoff', 'stormwater', 'geotracker', 'cameron']

print("=== SEARCHING REPOSITORY FOR NICHOLS MD INTERIOR RUNOFF EVIDENCE ===")
matches = []

for f in root.glob('**/*.*'):
    if f.is_file() and f.suffix in ['.txt', '.json', '.md', '.csv', '.pdf']:
        path_str = str(f)
        if 'opencode_work' in path_str or '.git' in path_str or 'copilot-worktrees' in path_str:
            continue
        try:
            content = f.read_text(encoding='utf-8', errors='ignore')
            content_lower = content.lower()
            if 'nichols' in content_lower or 'interior runoff' in content_lower or 'runoff' in content_lower:
                for line in content.splitlines():
                    line_lower = line.lower()
                    if any(k in line_lower for k in target_keywords):
                        matches.append({
                            'source': f.name,
                            'path': str(f),
                            'snippet': line.strip()[:200]
                        })
                        if len(matches) >= 30:
                            break
        except Exception:
            pass

out_file = root / 'data' / 'nichols_md_interior_runoff_search.json'
out_file.write_text(json.dumps(matches, indent=2), encoding='utf-8')

print(f"✓ Total Matches Found for Nichols MD / Runoff: {len(matches)}")
print(f"✓ Saved search results to: {out_file}\n")

print("Top Search Matches:")
for m in matches[:15]:
    print(f"[{m['source']}]: {m['snippet'][:120]}")
