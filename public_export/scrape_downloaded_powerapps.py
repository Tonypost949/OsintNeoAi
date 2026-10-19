import re
import json

filepath = r"C:\Users\Amd949609\Downloads\Power Apps _ Apps.html"

with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

print("=== SCRAPED POWER APPS HTML DATA AUDIT ===")

# Search for app names and metadata strings
names = set(re.findall(r'"displayName"\s*:\s*"([^"]+)"', content))
app_ids = set(re.findall(r'"name"\s*:\s*"([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})"', content))

print("\nDiscovered App Names:")
for n in sorted(list(names)):
    if any(k in n.lower() for k in ['osint', 'studio', 'manager', 'copilot', 'vibe', 'app', 'agent']):
        print(f" • {n}")

print("\nDiscovered App GUIDs:")
for a in sorted(list(app_ids)):
    print(f" • {a}")
