import re
from bs4 import BeautifulSoup

html_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\.system_generated\steps\855\content.md"

with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

print("Parsing content with BeautifulSoup...")
soup = BeautifulSoup(content, 'html.parser')

# Let's find all links
links = soup.find_all('a')
print(f"Found {len(links)} links.")
for i, link in enumerate(links[:30]):
    print(f"Link {i}: text={link.get_text().strip()}, href={link.get('href')}")

# Let's find all tables and their rows
tables = soup.find_all('table')
print(f"Found {len(tables)} tables.")
for idx, table in enumerate(tables):
    rows = table.find_all('tr')
    print(f"Table {idx} has {len(rows)} rows.")
    for r_idx, row in enumerate(rows[:10]):
        cols = [col.get_text().strip() for col in row.find_all(['td', 'th'])]
        print(f"  Row {r_idx}: {cols[:5]}")

# Let's search for divs with specific data attributes or classes
# In Google Drive, files often have classes like "e-s-v" or similar
# Let's search for any div or element with aria-label or data-label
print("\nSearching for aria-label or data-label or elements with text:")
for element in soup.find_all(attrs={"aria-label": True}):
    print(f"aria-label: {element['aria-label']} (tag: {element.name})")

for element in soup.find_all(attrs={"data-label": True}):
    print(f"data-label: {element['data-label']} (tag: {element.name})")

# Let's search for links that look like file/folder resource links:
# e.g., href="/drive/folders/..." or "/file/d/..."
print("\nSearching for drive links in href:")
for link in links:
    href = link.get('href', '')
    if href and ('drive/folders' in href or 'file/d' in href or 'open?id=' in href):
        print(f"- Text: {link.get_text().strip()} | Href: {href}")
