import json
from pathlib import Path

root = Path(r'C:\OsintNeoAi')
g_file = root / 'archive' / 'OsintNeoAi-Copy-1' / 'gmail_amd949609_hits.json'

if g_file.exists():
    data = json.loads(g_file.read_text(encoding='utf-8', errors='ignore'))
    print(f"TOTAL GMAIL EMAIL HITS IN ARCHIVE: {len(data)}\n")
    for i, d in enumerate(data[:30]):
        dt = d.get('date', 'N/A')
        subj = d.get('subject', 'N/A')
        frm = d.get('from_user', 'N/A')
        snip = d.get('snippet', '')[:140]
        print(f"[{i+1}] Date: {dt}")
        print(f"    From: {frm}")
        print(f"    Subject: {subj}")
        print(f"    Snippet: {snip}\n")
else:
    print(f"File not found: {g_file}")
