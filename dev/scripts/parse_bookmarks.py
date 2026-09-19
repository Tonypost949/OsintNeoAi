import json
import re
from pathlib import Path

root = Path(r'C:\OsintNeoAi')
desktop = Path(r'C:\Users\Amd949609\Desktop')

b_files = [root / 'chrome_bookmarks_dump.json'] + \
          list((root / 'cli' / 'data' / 'knowledge').glob('bookmarks*.json')) + \
          [desktop / 'firefoxbookmarks.html',
           desktop / 'djffoxbookmarks.html',
           desktop / 'txtdjffoxbookmarks-2026-08-12.json'] + \
          list((desktop / 'Old Firefox Data').glob('**/*bookmark*'))

all_links = []
for f in b_files:
    if f.exists() and f.is_file():
        content = f.read_text(encoding='utf-8', errors='ignore')
        matches = re.findall(r'https?://[^\s"\']+', content)
        all_links.extend(matches)

unique_links = sorted(list(set(all_links)))

out_file = root / 'data' / 'all_extracted_bookmarks.json'
out_file.parent.mkdir(parents=True, exist_ok=True)
out_file.write_text(json.dumps(unique_links, indent=2), encoding='utf-8')

print(f"UPDATED MASTER BOOKMARK INDEX: {len(unique_links)} TOTAL UNIQUE URLS")
