import json
import os

bookmarks_path = r"C:\Users\HP\AppData\Local\Google\Chrome\User Data\Profile 10\Bookmarks"

if not os.path.exists(bookmarks_path):
    print("Bookmarks file not found!")
    exit(1)

with open(bookmarks_path, 'r', encoding='utf-8', errors='ignore') as f:
    bookmarks_data = json.load(f)

print("=== USER CHROME BOOKMARKS ===")

def parse_node(node, path=""):
    if node.get("type") == "url":
        url = node.get("url", "")
        name = node.get("name", "")
        safe_name = name.encode('ascii', errors='ignore').decode()
        # Print if it contains keywords related to the case or general research
        print(f"[URL] {safe_name[:60]:<60} | {url}")
    elif node.get("type") == "folder":
        folder_name = node.get("name", "")
        children = node.get("children", [])
        new_path = f"{path} > {folder_name}" if path else folder_name
        for child in children:
            parse_node(child, new_path)

# Roots are: bookmark_bar, other, synced
roots = bookmarks_data.get("roots", {})
for root_name, root_node in roots.items():
    print(f"\n[ROOT] Root: {root_name.upper()}")
    parse_node(root_node)
