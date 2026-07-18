import re

html_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\.system_generated\steps\855\content.md"

with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Let's print some lines of the file to see what the markdown looks like
lines = content.splitlines()
print(f"Total lines: {len(lines)}")
print("First 50 lines:")
for i in range(min(50, len(lines))):
    print(f"{i+1}: {lines[i][:150]}")

print("\nSearching for mentions of 'APT2024' or 'china' or 'spy' or similar terms:")
for i, line in enumerate(lines):
    if any(term in line.lower() for term in ["apt2024", "spy", "china"]):
        print(f"Line {i+1}: {line[:200]}")

print("\nSearching for any links or IDs...")
# Let's look for pattern like drive.google.com/file/d/ or similar
drive_links = re.findall(r'https://drive\.google\.com/file/d/[a-zA-Z0-9_-]+', content)
print(f"Found {len(drive_links)} direct drive file links:")
for link in set(drive_links):
    print(f"- {link}")

# Let's search for patterns in the JSON or raw data
# Often file list is in window._INITIAL_DATA or some JSON block
# Let's see if we can extract JSON blocks
json_blocks = re.findall(r'(\{.*?\})', content)
print(f"\nFound {len(json_blocks)} potential JSON blocks.")
