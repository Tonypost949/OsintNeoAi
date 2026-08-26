import json, re

html_file = r'C:\Users\Amd949609\.gemini\antigravity-cli\brain\e0259c57-0b03-45f8-956f-927ea22d1195\.system_generated\steps\5789\content.md'
with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

matches = re.findall(r'>([^<]+)<', text)
print(f'Total HTML text nodes: {len(matches)}')
seen = set()
for m in matches:
    clean = m.strip().replace('&amp;', '&').replace('&nbsp;', ' ')
    if clean and clean not in seen and len(clean) > 2 and not clean.startswith('@') and not clean.startswith('{'):
        seen.add(clean)
        print('->', clean)
