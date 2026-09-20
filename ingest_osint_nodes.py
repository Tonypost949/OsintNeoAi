import json
import csv
import os

# Load scraped bookmarks
with open('C:/OsintNeoAi/scraped_system_bookmarks.json', 'r', encoding='utf-8') as f:
    bookmarks = json.load(f)

# Ensure user folder exists
user_dir = 'C:/Amd949609_Antigravity_v1'
os.makedirs(user_dir, exist_ok=True)
nodes_csv = os.path.join(user_dir, 'user_nodes.csv')

# Backup existing user_nodes.csv if present
if os.path.exists(nodes_csv):
    with open(nodes_csv, 'r', encoding='utf-8') as f:
        existing_content = f.read()
    with open(nodes_csv + '.bak', 'w', encoding='utf-8') as f:
        f.write(existing_content)

# Define mandatory OSINT categories
osint_categories = {
    'search': ['google', 'bing', 'duckduckgo', 'yandex', 'baidu', 'shodan', 'censys', 'virustotal'],
    'social': ['facebook', 'twitter', 'x.com', 'linkedin', 'instagram', 'github', 'reddit', 'telegram'],
    'cloud_msft': ['powerapps', 'azure', 'microsoft', 'office', 'onedrive', 'copilotstudio', 'vibe.powerapps'],
    'cloud_google': ['drive.google', 'gmail', 'gemini.google', 'console.cloud.google', 'photos.google'],
    'records_osint': ['county', 'court', 'permit', 'property', 'tax', 'state', 'gov', 'hud']
}

nodes = []

for b in bookmarks:
    u = b.get('url', '')
    t = b.get('title', b.get('name', 'Bookmark'))
    src = b.get('source', 'Harvested')
    if not u:
        continue

    # Determine node type
    node_type = 'General Bookmark'
    for cat, keywords in osint_categories.items():
        if any(k in u.lower() for k in keywords):
            node_type = f'OSINT Tool ({cat})'
            break

    nodes.append({
        'Label': t,
        'URL': u,
        'Type': node_type,
        'Source': src
    })

# Write to user_nodes.csv
with open(nodes_csv, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['Label', 'URL', 'Type', 'Source'])
    writer.writeheader()
    writer.writerows(nodes)

print(f"Successfully ingested {len(nodes)} OSINT tool & bookmark nodes into {nodes_csv}")
