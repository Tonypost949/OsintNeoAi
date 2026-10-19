import os
import re
import zipfile
from pathlib import Path

print("=== Checking zip files for contained documents / mailboxes ===")
downloads_dir = "C:\\Users\\Amd949609\\Downloads"
for f in os.listdir(downloads_dir):
    if f.lower().endswith(".zip"):
        full_p = os.path.join(downloads_dir, f)
        try:
            with zipfile.ZipFile(full_p, 'r') as z:
                names = z.namelist()
                doc_matches = [n for n in names if any(n.lower().endswith(ext) for ext in ['.pdf', '.eml', '.msg', '.mbox', '.html', '.htm', '.txt', '.json', '.csv', '.tif', '.jpg', '.png'])]
                if doc_matches:
                    print(f"\nZip: {f} (Total entries: {len(names)}, Document entries: {len(doc_matches)})")
                    for m in doc_matches[:10]:
                        print(f"  -> {m}")
                    if len(doc_matches) > 10:
                        print(f"  ... and {len(doc_matches)-10} more")
        except Exception as e:
            print(f"Error reading zip {f}: {e}")

print("\n=== Checking for .eml, .msg, .mbox in evidence and repo ===")
for base in ["C:\\OsintNeoAi", "C:\\Users\\Amd949609\\Downloads"]:
    for root, dirs, files in os.walk(base):
        if ".git" in root or ".gemini" in root:
            continue
        for f in files:
            ext = Path(f).suffix.lower()
            if ext in [".eml", ".msg", ".mbox"]:
                print(f"Found mail file: {os.path.join(root, f)}")

print("\n=== Searching for external Google Drive links in evidence & repo ===")
gdrive_regex = re.compile(r'https?://(?:drive|docs)\.google\.com/[^\s\'"\)\]]+')
found_links = set()
for base in ["C:\\OsintNeoAi\\evidence", "C:\\OsintNeoAi\\agent", "C:\\OsintNeoAi\\core"]:
    for root, dirs, files in os.walk(base):
        for f in files:
            if f.endswith(('.md', '.json', '.py', '.txt', '.csv')):
                p = os.path.join(root, f)
                try:
                    with open(p, 'r', encoding='utf-8', errors='ignore') as fh:
                        content = fh.read()
                        matches = gdrive_regex.findall(content)
                        for m in matches:
                            found_links.add((m, os.path.relpath(p, "C:\\OsintNeoAi")))
                except Exception:
                    pass

for link, src in list(found_links)[:25]:
    print(f"GDrive link: {link} (in {src})")
print(f"Total unique GDrive links found: {len(found_links)}")
