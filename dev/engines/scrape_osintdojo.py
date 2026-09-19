import os
import json
import urllib.request
from bs4 import BeautifulSoup
import shutil

# Target files
tools_json_path = os.path.join("C:\\osintneoai\\cli\\data", "tools.json")

print("[*] Starting autonomous extraction from osintdojo.com/resources/...")

# 1. Fetch the OSINT Dojo resources page
url = "https://www.osintdojo.com/resources/"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    response = urllib.request.urlopen(req)
    html = response.read().decode('utf-8')
except Exception as e:
    print(f"[-] Failed to fetch OSINT Dojo: {e}")
    exit(1)

soup = BeautifulSoup(html, "html.parser")

# 2. Parse categories and links
extracted_tools = []
current_category = "General"

for element in soup.find_all(['h2', 'h3', 'h4', 'a']):
    if element.name in ['h2', 'h3', 'h4']:
        cat_name = element.get_text(strip=True)
        if cat_name and len(cat_name) < 50:
            current_category = cat_name
    elif element.name == 'a':
        href = element.get('href', '').strip()
        name = element.get_text(strip=True)
        if href.startswith('http') and len(name) > 2 and 'osintdojo.com' not in href:
            extracted_tools.append({
                "name": name,
                "url": href,
                "category": current_category,
                "description": f"OSINT Dojo Resource: {current_category}"
            })

print(f"[+] Extracted {len(extracted_tools)} tools from OSINT Dojo.")

if len(extracted_tools) == 0:
    print("[-] No tools extracted. Verify page structure.")
    exit(1)

# 3. Read existing tools.json
existing_data = {"tools": []}
if os.path.exists(tools_json_path):
    with open(tools_json_path, "r", encoding="utf-8") as f:
        existing_data = json.load(f)

# 4. Create Reversible Backup (Rule 11)
backup_path = tools_json_path + ".bak"
if os.path.exists(tools_json_path):
    shutil.copy2(tools_json_path, backup_path)
    print(f"[+] Created reversible backup at {backup_path}")

# 5. Merge and deduplicate
existing_urls = {t.get("url", "").lower().strip() for t in existing_data.get("tools", []) if t.get("url")}
existing_names = {t.get("name", "").lower().strip() for t in existing_data.get("tools", []) if t.get("name")}

added_count = 0
for tool in extracted_tools:
    t_url = tool["url"].lower()
    t_name = tool["name"].lower()
    if t_url not in existing_urls and t_name not in existing_names:
        existing_data["tools"].append(tool)
        existing_urls.add(t_url)
        existing_names.add(t_name)
        added_count += 1

# 6. Save updated tools.json
with open(tools_json_path, "w", encoding="utf-8") as f:
    json.dump(existing_data, f, indent=2)

print(f"[+] Successfully merged {added_count} new tools into {tools_json_path}.")
print(f"[+] Total tools now in registry: {len(existing_data['tools'])}")
