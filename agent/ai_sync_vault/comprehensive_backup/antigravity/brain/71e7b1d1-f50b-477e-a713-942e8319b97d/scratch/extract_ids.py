import re

html_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\.system_generated\steps\934\content.md"

with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Let's search for occurrences of each folder name and find the closest 33-character Google Drive ID.
# GDrive IDs look like: 1-4u-88uTqj-pLRGKzpSSbS7KsieWUBb8 or other 28-40 char alphanumeric strings containing dashes or underscores.
# Let's search the HTML around each name.
folder_names = [
    "combine test 1 (full list)",
    "combine test 1 (trimmed)",
    "LOG",
    "MD",
    "ORIGINAL",
    "PNG",
    "TXT"
]

print("Extracting folder names and their closest IDs in the HTML content:")
for name in folder_names:
    print(f"\n--- {name} ---")
    # Let's find all indices of this name in the text
    indices = [m.start() for m in re.finditer(re.escape(name), content)]
    for idx in indices:
        # Get a context of 1000 characters around the match
        start_ctx = max(0, idx - 500)
        end_ctx = min(len(content), idx + 500)
        context = content[start_ctx:end_ctx]
        
        # Search for Drive IDs in this context
        ids = re.findall(r'"([a-zA-Z0-9_-]{28,40})"', context)
        # Filter out non-ID patterns
        ids = [fid for fid in ids if any(c.islower() for c in fid) and any(c.isupper() for c in fid) and any(c.isdigit() for c in fid) and not fid.startswith("AIzaSy")]
        print(f"Match context index {idx}. Found potential IDs: {list(set(ids))}")
