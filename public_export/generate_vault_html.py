import json
import html

with open('C:/OsintNeoAi/scraped_system_bookmarks.json', 'r', encoding='utf-8') as f:
    bookmarks = json.load(f)

# Filter key Google, Microsoft, Power Platform, Azure, GitHub, and cloud account bookmarks
filtered = []
seen = set()
for b in bookmarks:
    url = b.get('url', '')
    title = b.get('name', b.get('title', 'Bookmark'))
    if not url or url in seen:
        continue
    if any(k in url.lower() for k in ['google.com', 'powerapps.com', 'microsoft.com', 'azure.com', 'office.com', 'office365.com', 'onedrive', 'github.com', 'vibe.powerapps.com', 'copilotstudio', 'gmail.com', 'drive.google.com']):
        seen.add(url)
        filtered.append({'title': title, 'url': url, 'source': b.get('source', 'Browser')})

print(f"Total Account Specific Bookmarks Filtered: {len(filtered)}")

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Universal Account Bookmarks Vault (17,006 Total Harvested)</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #0a0e17; color: #f3f4f6; padding: 24px; margin: 0; }
        h1 { color: #00d2ff; font-size: 1.8rem; margin-top: 0; }
        .stats-badge { background: #1a233a; border: 1px solid #2d3748; padding: 8px 16px; border-radius: 20px; font-size: 0.9rem; color: #4ade80; display: inline-block; margin-bottom: 20px; }
        .search-box { width: 100%; padding: 12px 16px; margin-bottom: 24px; background: #131b2e; border: 1px solid #2d3748; color: #fff; border-radius: 8px; font-size: 1rem; box-sizing: border-box; }
        .search-box:focus { outline: none; border-color: #00d2ff; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 16px; }
        .card { background: #1a233a; border: 1px solid #2d3748; padding: 16px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
        .title { font-weight: 600; color: #ffffff; font-size: 1rem; display: block; margin-bottom: 6px; }
        .url { color: #00d2ff; font-size: 0.85rem; word-break: break-all; display: block; margin-bottom: 8px; font-family: Consolas, monospace; }
        .badge { background: #0078d4; color: #fff; padding: 2px 8px; font-size: 0.75rem; border-radius: 4px; font-weight: 600; }
        a.btn { display: inline-block; background: #0078d4; color: #fff; padding: 6px 12px; text-decoration: none; border-radius: 4px; font-size: 0.85rem; margin-top: 8px; font-weight: 500; }
        a.btn:hover { background: #005a9e; }
    </style>
</head>
<body>
    <h1>📌 Universal Account Bookmarks Vault</h1>
    <div class="stats-badge">Total Harvested System Bookmarks: 17,006 | Account & Cloud Items Index: """ + str(len(filtered)) + """</div>
    <input type="text" class="search-box" id="searchInput" onkeyup="filter()" placeholder="🔍 Search 17,006 account bookmarks, Google Drive files, PowerApps, Azure, Gmail, Office 365...">
    <div class="grid" id="container">
"""

for b in filtered:
    t = html.escape(b['title'])
    u = html.escape(b['url'])
    src = html.escape(b['source'])
    html_content += f"""
        <div class="card">
            <span class="title">{t}</span>
            <span class="url">{u}</span>
            <span class="badge">{src}</span>
            <br>
            <a class="btn" href="{u}" target="_blank">Open Bookmark</a>
        </div>
    """

html_content += """
    </div>
    <script>
        function filter() {
            let input = document.getElementById('searchInput').value.toLowerCase();
            let cards = document.getElementsByClassName('card');
            for (let c of cards) {
                c.style.display = c.innerText.toLowerCase().includes(input) ? '' : 'none';
            }
        }
    </script>
</body>
</html>
"""

with open('C:/OsintNeoAi/Universal_Account_Bookmarks_Vault.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Universal Vault HTML successfully generated with {len(filtered)} items.")
