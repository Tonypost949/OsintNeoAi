import re
from bs4 import BeautifulSoup

html_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\.system_generated\steps\855\content.md"

with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

soup = BeautifulSoup(content, 'html.parser')

# Let's find elements that contain "APT2024filesfull"
for element in soup.find_all(text=re.compile("APT2024filesfull")):
    print(f"Text match: '{element}'")
    parent = element.parent
    print(f"Parent tag: {parent.name}, attrs: {parent.attrs}")
    grandparent = parent.parent
    print(f"Grandparent tag: {grandparent.name}, attrs: {grandparent.attrs}")
    # Let's print the outer HTML of the grandparent
    print(f"HTML snippet: {grandparent.prettify()[:1000]}")
    print("-" * 50)

# Let's search for any Google Drive ID strings in the entire HTML page
# They are typically 33 characters (sometimes 28 to 40) alphanumeric strings.
# The folder ID we know is "173mY5p0bvl_2SjiGdmExkoOKDYgj_loN"
# Let's find all alphanumeric strings of length 28-40 that contain underscores or hyphens and are in quotes
potential_ids = re.findall(r'"([a-zA-Z0-9_-]{28,40})"', content)
print(f"Found {len(set(potential_ids))} unique potential IDs:")
for fid in sorted(set(potential_ids)):
    # Let's filter out known non-id things like API keys (AIzaSy...) or others
    if not fid.startswith("AIzaSy") and fid != "173mY5p0bvl_2SjiGdmExkoOKDYgj_loN":
        # Check if it has both lowercase, uppercase, and numbers (typical of GDrive IDs)
        if any(c.islower() for c in fid) and any(c.isupper() for c in fid) and any(c.isdigit() for c in fid):
            print(f"- {fid}")
