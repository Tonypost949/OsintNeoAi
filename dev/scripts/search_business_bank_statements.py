import os
import json
import re
from pathlib import Path

root = Path(r'C:\OsintNeoAi')
target_terms = [
    'atlas', 'cabinets', 'statement', 'bank', 'chase', 'account', 'checking',
    'deposit', 'balance', 'revenue', 'profit', 'tax', '1099', 'w2', 'schedule c',
    'payoff', 'money order', 'assistance'
]

print("=== SEARCHING REPOSITORY FOR BUSINESS BANK STATEMENTS & FINANCIAL RECORDS ===")
matches = []

for f in root.glob('**/*.*'):
    if f.is_file() and f.suffix in ['.json', '.txt', '.csv', '.md', '.pdf']:
        path_str = str(f)
        if 'opencode_work' in path_str or '.git' in path_str or 'copilot-worktrees' in path_str:
            continue
        try:
            content = f.read_text(encoding='utf-8', errors='ignore')
            content_lower = content.lower()
            if 'atlas' in content_lower and ('statement' in content_lower or 'bank' in content_lower or 'chase' in content_lower or 'account' in content_lower or 'deposit' in content_lower):
                for line in content.splitlines():
                    line_lower = line.lower()
                    if any(t in line_lower for t in ['statement', 'chase', 'bank', 'balance', 'deposit', 'account']):
                        matches.append({
                            'source': f.name,
                            'path': str(f),
                            'snippet': line.strip()[:200]
                        })
                        if len(matches) >= 30:
                            break
        except Exception:
            pass

out_file = root / 'data' / 'business_bank_statements_search.json'
out_file.write_text(json.dumps(matches, indent=2), encoding='utf-8')

print(f"✓ Total Financial / Business Bank Statement Matches Found: {len(matches)}")
print(f"✓ Saved to: {out_file}\n")

print("Top Bank Statement Matches:")
for m in matches[:15]:
    print(f"[{m['source']}]: {m['snippet'][:120]}")
