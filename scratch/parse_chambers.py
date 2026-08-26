import re

file_path = r'C:\Users\Amd949609\.gemini\antigravity-cli\brain\e0259c57-0b03-45f8-956f-927ea22d1195\.system_generated\steps\6260\content.md'
with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

md_links = re.findall(r'\[([^\]]+)\]\((https?://[^\)]+|/[^\)]+)\)', text)
html_links = re.findall(r'<a\s+(?:[^>]*?\s+)?href="([^"]*)"[^>]*>(.*?)</a>', text, flags=re.DOTALL)

all_links = []
seen = set()

for title, url in md_links:
    clean_t = title.strip()
    clean_u = url.strip()
    if clean_u.startswith('/'):
        clean_u = 'https://www.ocgov.com' + clean_u
    if clean_u not in seen and len(clean_t) > 2 and 'theme' not in clean_u and 'privacy' not in clean_t.lower():
        seen.add(clean_u)
        all_links.append({"title": clean_t, "url": clean_u})

for url, title in html_links:
    clean_t = re.sub(r'<[^>]+>', '', title).strip()
    clean_u = url.strip()
    if clean_u.startswith('/'):
        clean_u = 'https://www.ocgov.com' + clean_u
    if clean_u not in seen and len(clean_t) > 2 and 'theme' not in clean_u and 'privacy' not in clean_t.lower():
        seen.add(clean_u)
        all_links.append({"title": clean_t, "url": clean_u})

print(f"Total extracted Chambers of Commerce links: {len(all_links)}")
for l in all_links:
    print(f" - {l['title']}: {l['url']}")
