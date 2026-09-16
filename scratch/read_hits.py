import json
from pathlib import Path

with open(r'C:\OsintNeoAi\scratch\extraction_results.json', encoding='utf-8') as f:
    d = json.load(f)

# Top legal hits
print('=== TOP LEGAL HITS (first 20) ===')
for h in d['raw_text_hits'].get('legal', [])[:20]:
    fpath = h.get('file', '')
    snippet = h.get('snippet', '')[:200]
    print(f'[{fpath}]')
    print(f'  {snippet}')
    print()

print('=== TOP CYBER HITS (first 20) ===')
for h in d['raw_text_hits'].get('cyber', [])[:20]:
    fpath = h.get('file', '')
    snippet = h.get('snippet', '')[:200]
    print(f'[{fpath}]')
    print(f'  {snippet}')
    print()

print('=== TOP ENVIRONMENTAL HITS (first 20) ===')
for h in d['raw_text_hits'].get('environmental', [])[:20]:
    fpath = h.get('file', '')
    snippet = h.get('snippet', '')[:200]
    print(f'[{fpath}]')
    print(f'  {snippet}')
    print()

print('=== TOP FINANCIAL HITS (first 20) ===')
for h in d['raw_text_hits'].get('financial', [])[:20]:
    fpath = h.get('file', '')
    snippet = h.get('snippet', '')[:200]
    print(f'[{fpath}]')
    print(f'  {snippet}')
    print()

print('=== BRIEFINGS ===')
for b in d['raw_text_hits'].get('briefings', [])[:10]:
    fpath = b.get('file', '')
    content = b.get('content', '')[:400]
    print(f'[{fpath}]')
    print(content)
    print()

print('=== REPORTS ===')
for r in d['raw_text_hits'].get('reports', [])[:10]:
    fpath = r.get('file', '')
    content = r.get('content', '')[:400]
    print(f'[{fpath}]')
    print(content)
    print()
