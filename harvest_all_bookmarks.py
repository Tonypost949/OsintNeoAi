import glob
import os
import json
import re

bookmarks = []

# Scan Chrome Bookmarks
chrome_paths = glob.glob(os.path.expanduser('~') + '/AppData/Local/Google/Chrome/User Data/*/Bookmarks') + glob.glob(os.path.expanduser('~') + '/AppData/Local/Google/Chrome/User Data/Bookmarks')
for cp in chrome_paths:
    try:
        with open(cp, 'r', encoding='utf-8', errors='ignore') as f:
            data = json.load(f)
            def recurse_chrome(node):
                if isinstance(node, dict):
                    if node.get('type') == 'url':
                        bookmarks.append({'title': node.get('name'), 'url': node.get('url'), 'source': 'Chrome (' + cp + ')'})
                    for k, v in node.items():
                        recurse_chrome(v)
                elif isinstance(node, list):
                    for item in node:
                        recurse_chrome(item)
            recurse_chrome(data)
    except Exception as e:
        pass

# Scan Edge Bookmarks
edge_paths = glob.glob(os.path.expanduser('~') + '/AppData/Local/Microsoft/Edge/User Data/*/Bookmarks') + glob.glob(os.path.expanduser('~') + '/AppData/Local/Microsoft/Edge/User Data/Bookmarks')
for ep in edge_paths:
    try:
        with open(ep, 'r', encoding='utf-8', errors='ignore') as f:
            data = json.load(f)
            def recurse_edge(node):
                if isinstance(node, dict):
                    if node.get('type') == 'url':
                        bookmarks.append({'title': node.get('name'), 'url': node.get('url'), 'source': 'Edge (' + ep + ')'})
                    for k, v in node.items():
                        recurse_edge(v)
                elif isinstance(node, list):
                    for item in node:
                        recurse_edge(item)
            recurse_edge(data)
    except Exception as e:
        pass

# Scan local downloads & project files for HTML bookmarks or exported link files
search_dirs = ['C:/OsintNeoAi', os.path.expanduser('~') + '/Downloads']
for sdir in search_dirs:
    for root, dirs, files in os.walk(sdir):
        for file in files:
            if file.endswith('.html') or file.endswith('.htm') or file.endswith('.json'):
                fp = os.path.join(root, file)
                try:
                    with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        urls = re.findall(r'href=["\'](https?://[^\'"]+)["\']', content)
                        for u in set(urls):
                            bookmarks.append({'title': file, 'url': u, 'source': 'Backup/File (' + fp + ')'})
                except Exception:
                    pass

print(f"Total Bookmarks & Favorites Discovered: {len(bookmarks)}")

# Deduplicate by URL
unique_bookmarks = {}
for b in bookmarks:
    if b['url'] not in unique_bookmarks:
        unique_bookmarks[b['url']] = b

deduped = list(unique_bookmarks.values())
print(f"Total Unique Bookmarks: {len(deduped)}")

with open('C:/OsintNeoAi/scraped_system_bookmarks.json', 'w', encoding='utf-8') as f:
    json.dump(deduped, f, indent=2)
