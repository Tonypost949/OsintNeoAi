import re
import json

filepath = r"C:\Users\Amd949609\Downloads\Power Apps _ Apps.html"

with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
    html_content = f.read()

guids = set(re.findall(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', html_content, re.IGNORECASE))
print("=== DISCOVERED POWER APPS & ENVIRONMENT GUIDS ===")
for g in guids:
    print(f" - {g}")

print("\n=== EXTRACTED POWERAPPS URLs & ENDPOINTS ===")
urls = set(re.findall(r'https://[a-zA-Z0-9\.\/\?%\&=\-_]+', html_content))
for u in sorted(list(urls)):
    if 'powerapps' in u or 'dynamics' in u or 'play' in u or 'vibe' in u:
        print(f" - {u}")
