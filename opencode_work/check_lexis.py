import pathlib, json, re
kb_path = pathlib.Path(r"C:\OsintNeoAi\knowledge_base\post_bookmarks_knowledge_v1.json")
kb_text = kb_path.read_text(encoding="utf-8")
data = json.loads(kb_text)
lexis = [l for l in data['all_links'] if 'lexis' in l['url'].lower()]
print(f"lexis count {len(lexis)}")
for l in lexis[:10]:
    print(l['url'], "|", l['title'], "|", l['folder_hierarchy'])

target='https://nexis.lexisnexis.com/aisearch/chat/819adcf0-2b9a-4c84-8501-3b789be09ca9'
print("target in kb?", target in kb_text)

html_path = pathlib.Path(r"C:\Users\Amd949609\Documents\POST82526favorites_8_25_26.html")
html = html_path.read_text(encoding="utf-8", errors="ignore")
print("target in html?", target in html)
print("advance.lexis in html?", "advance.lexis.com" in html)
hrefs = re.findall(r'HREF="([^"]*lexis[^"]*)"', html, flags=re.I)
print("hrefs with lexis:", hrefs[:10])
# also check nexis
nexis_hrefs = re.findall(r'HREF="([^"]*nexis[^"]*)"', html, flags=re.I)
print("nexis hrefs:", nexis_hrefs[:10])

# check OSINT tools catalog
