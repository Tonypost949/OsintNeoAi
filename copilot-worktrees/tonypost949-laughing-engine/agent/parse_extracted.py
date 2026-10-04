from bs4 import BeautifulSoup
import re

with open("unclaimed_property_raw.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("=== Text Extraction Check ===")
# Print lines containing key terms
text = soup.get_text()
for line in text.split('\n'):
    line = line.strip()
    if line and any(term in line.lower() for term in ['mercy', 'haynes', 'house', 'claim', 'property', 'owner', 'found']):
        print("  ", line)

print("\n=== Elements Check ===")
# Search for table rows or table elements
rows = soup.find_all(['tr', 'li', 'div', 'p'])
matches = []
for r in rows:
    t = r.get_text().strip()
    if t and any(term in t.lower() for term in ['mercy', 'haynes', 'house']) and len(t) < 500:
        if t not in matches:
            matches.append(t)

for m in matches:
    print("-" * 50)
    print(m)
