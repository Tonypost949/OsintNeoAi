import re

file_path = r'C:\Users\Amd949609\.gemini\antigravity-cli\brain\e0259c57-0b03-45f8-956f-927ea22d1195\.system_generated\steps\6260\content.md'
with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

anchors = re.findall(r'<a\s+[^>]*href="([^"]+)"[^>]*>(.*?)</a>', text, re.IGNORECASE | re.DOTALL)
print(f"Total anchors: {len(anchors)}")
for href, label in anchors:
    clean_l = re.sub(r'<[^>]+>', '', label).strip()
    if any(k in href.lower() or k in clean_l.lower() for k in ['chamber', 'anaheim', 'irvine', 'costa', 'newport', 'huntington', 'fullerton', 'orange', 'mission', 'laguna', 'buena', 'santa ana']):
        print(f" - {clean_l} -> {href}")
