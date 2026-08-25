import os
import re

base = r'C:\Users\Amd949609\OsintNeoAi-1'
gdrive_matches = []
all_unique_urls = set()

for root, dirs, files in os.walk(base):
    for f in files:
        if f.endswith(('.md', '.html', '.json', '.txt', '.py')):
            fp = os.path.join(root, f)
            try:
                with open(fp, 'r', encoding='utf-8', errors='ignore') as fh:
                    content = fh.read()
                    if 'drive.google.com' in content or 'docs.google.com' in content:
                        urls = re.findall(r'https?://(?:drive|docs)\.google\.com/[^\s"\'<>\)]+', content)
                        if urls:
                            gdrive_matches.append({'file': fp, 'urls': list(set(urls))})
                            for u in urls:
                                all_unique_urls.add(u)
            except Exception:
                pass

print(f"Files containing Google Drive links: {len(gdrive_matches)}")
for m in gdrive_matches:
    print(f"\nFile: {m['file']}")
    for u in m['urls']:
        print(f"  • {u}")

print(f"\n==========================================")
print(f"TOTAL UNIQUE GOOGLE DRIVE URLS: {len(all_unique_urls)}")
print(f"==========================================")
for u in sorted(all_unique_urls):
    print(u)
