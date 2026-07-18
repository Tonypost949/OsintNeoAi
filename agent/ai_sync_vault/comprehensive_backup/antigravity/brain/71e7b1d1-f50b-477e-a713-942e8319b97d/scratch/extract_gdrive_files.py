import re
import json

html_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\.system_generated\steps\855\content.md"

print("Reading HTML file...")
with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

# Let's search for file patterns or arrays
print("Searching for file arrays in INITIAL_DATA or bootstrapped JSON...")

# In Google Drive, folder files are bootstrapped in arrays like:
# ["id", "name", "mimeType", ...]
# Let's search for matches using regex. Common IDs in Google Drive are 33-character alphanumeric strings.
# Let's search for patterns that look like Google Drive file IDs and their surrounding titles.
matches = re.findall(r'\["[a-zA-Z0-9_-]{28,40}",\s*"[^"]+?"', html)
for m in matches:
    print(f"Potential file/folder metadata: {m}")

# Let's also do a general search for string patterns containing typical file extensions like .xlsx, .pdf, .docx, .zip, .png, .txt
extensions = [r"\.xlsx", r"\.pdf", r"\.docx", r"\.zip", r"\.png", r"\.txt", r"\.jpg", r"\.csv", r"\.json"]
for ext in extensions:
    p = r'[^"\[\]\\/:\*\?<>|]+\b' + ext
    ext_matches = re.findall(p, html, re.IGNORECASE)
    if ext_matches:
        print(f"\nFound file names ending with {ext}:")
        for em in set(ext_matches):
            print(f"- {em.strip()}")

# Let's search for common Google Drive boot data structures
boot_data = re.findall(r'window\._INITIAL_DATA\s*=\s*(.*?);', html)
if boot_data:
    print(f"\nFound INITIAL_DATA block! Length: {len(boot_data[0])}")
    with open("boot_data.txt", "w", encoding='utf-8') as b_out:
        b_out.write(boot_data[0])
