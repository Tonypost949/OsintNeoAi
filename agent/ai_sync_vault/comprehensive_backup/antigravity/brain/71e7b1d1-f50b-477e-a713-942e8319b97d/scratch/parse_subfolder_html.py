import re
from bs4 import BeautifulSoup

html_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\.system_generated\steps\934\content.md"

with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

print("Parsing subfolder with BeautifulSoup...")
soup = BeautifulSoup(content, 'html.parser')

# Let's find all tables and their rows
tables = soup.find_all('table')
print(f"Found {len(tables)} tables.")
for idx, table in enumerate(tables):
    rows = table.find_all('tr')
    print(f"Table {idx} has {len(rows)} rows.")
    for r_idx, row in enumerate(rows[:50]):
        cols = [col.get_text().strip() for col in row.find_all(['td', 'th'])]
        print(f"  Row {r_idx}: {cols[:5]}")

# Let's search for elements with aria-label or data-label representing files
print("\nSearching for aria-label representing files:")
for element in soup.find_all(attrs={"aria-label": True}):
    al = element['aria-label']
    if any(keyword in al.lower() for keyword in ["shared", "modified", "size"]):
        print(f"- aria-label: {al} (tag: {element.name})")

# Let's find drive IDs
potential_ids = re.findall(r'"([a-zA-Z0-9_-]{28,40})"', content)
print(f"\nFound {len(set(potential_ids))} unique potential IDs.")

# Let's find AF_initDataCallback that bootstraps the files
# and see if we can print the files listed there
init_data_matches = re.findall(r'AF_initDataCallback\(\{key:\s*\'ds:4\'.*?data:\[2,.*?,null,\[(.*?)\]\s*,\s*sideChannel', content, re.DOTALL)
if init_data_matches:
    print("\nFound ds:4 initial data block!")
    # Let's write a python regex or json list search to extract all file names and IDs from this block
    raw_data = init_data_matches[0]
    # In Gdrive's ds:4 data, files are listed with names, types, and IDs.
    # We can match files and IDs by regex:
    # A filename often has extensions like pdf, xlsx, docx, zip, csv, png or is in quotes.
    # A file ID is 33 characters (with underscores/hyphens/caps).
    # Let's do a regex search for the filenames and their sibling IDs.
    # In the raw data, files are in lists of the form:
    # [[null,"ID"],null,null,null,"mimeType",...] and name is in a nested list: [null,[[["NAME",null,1]]]]
    # Let's search for matches of IDs:
    file_chunks = re.findall(r'\[\[null,"([a-zA-Z0-9_-]{28,40})"\],null,null,null,"([^"]+?)"(.*?)]\],More actions"', raw_data, re.DOTALL)
    print(f"Extracted {len(file_chunks)} raw file chunks.")
    
    # Alternatively, let's just find all occurrences of strings ending in common extensions or folder types
    # and all occurrences of file IDs.
    # Let's print out all lines in GDrive ds:4 matching known filenames:
    import json
    # Let's scan for name strings
    names = re.findall(r'\[\[\["([^"]+?)",null,1]]]', raw_data)
    ids = re.findall(r'\[null,"([a-zA-Z0-9_-]{28,40})"\],Download', raw_data)
    print(f"Extracted {len(names)} names and {len(ids)} download IDs.")
    for n, i in zip(names, ids):
        print(f"File: {n} | ID: {i}")
