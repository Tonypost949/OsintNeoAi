import os
import re
import json

HTML_PATH = r"C:\Users\Amd949609\Documents\POST82526favorites_8_25_26.html"
OUT_JSON = os.path.join("evidence", "post_favorites_8_25_26.json")
OUT_MD = os.path.join("legal_library", "POST_UNIVERSITY_FAVORITES_BOOKMARK_INDEX.md")

os.makedirs("evidence", exist_ok=True)
os.makedirs("legal_library", exist_ok=True)

print(f"[*] Reading bookmarks from: {HTML_PATH}")

if not os.path.exists(HTML_PATH):
    print(f"[-] File not found at {HTML_PATH}")
    exit(1)

with open(HTML_PATH, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

# Pattern for bookmarks and folders
bookmark_pattern = re.compile(r'<A\s+HREF="([^"]+)"[^>]*>(.*?)</A>', re.IGNORECASE)
folder_pattern = re.compile(r'<H3[^>]*>(.*?)</H3>', re.IGNORECASE)

bookmarks = bookmark_pattern.findall(content)
folders = folder_pattern.findall(content)

print(f"[+] Total Bookmarks Extracted: {len(bookmarks)}")
print(f"[+] Total Folders Extracted: {len(folders)}")

cleaned_bookmarks = []
categories = {
    "Blackboard & Post University": [],
    "LexisNexis & Legal Research": [],
    "EBSCOhost & Academic DBs": [],
    "ProQuest & Business Intel": [],
    "Government, Portals & General": []
}

for href, title in bookmarks:
    clean_title = re.sub(r'<[^>]+>', '', title).strip()
    if not clean_title:
        clean_title = href
    
    item = {"title": clean_title, "url": href}
    cleaned_bookmarks.append(item)
    
    href_lower = href.lower()
    title_lower = clean_title.lower()
    
    if "blackboard" in href_lower or "post.edu" in href_lower:
        categories["Blackboard & Post University"].append(item)
    elif "lexis" in href_lower or "nexis" in href_lower or "legal" in title_lower:
        categories["LexisNexis & Legal Research"].append(item)
    elif "ebsco" in href_lower or "cinahl" in href_lower or "eagles" in title_lower:
        categories["EBSCOhost & Academic DBs"].append(item)
    elif "proquest" in href_lower or "mergent" in href_lower or "statista" in href_lower:
        categories["ProQuest & Business Intel"].append(item)
    else:
        categories["Government, Portals & General"].append(item)

# Save JSON
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump({"total": len(cleaned_bookmarks), "folders": folders, "categories": categories, "bookmarks": cleaned_bookmarks}, f, indent=2)
print(f"[+] Saved structured JSON to: {OUT_JSON}")

# Generate Markdown Index
md_lines = [
    "# 📑 POST UNIVERSITY & ACADEMIC FAVORITES BOOKMARK INDEX (8/25/2026)",
    f"**Source File:** `{HTML_PATH}`  ",
    f"**Total Bookmarks Extracted:** `{len(cleaned_bookmarks)}` | **Folders:** `{len(folders)}`\n",
    "---\n"
]

for cat_name, items in categories.items():
    if items:
        md_lines.append(f"## 📁 {cat_name} ({len(items)} Links)\n")
        md_lines.append("| # | Resource Title | Destination URL |")
        md_lines.append("|---|---|---|")
        for i, it in enumerate(items, 1):
            md_lines.append(f"| {i} | **{it['title']}** | [`{it['url'][:60]}...`]({it['url']}) |")
        md_lines.append("\n---\n")

with open(OUT_MD, "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

print(f"[+] Generated Master Markdown Index at: {OUT_MD}")
