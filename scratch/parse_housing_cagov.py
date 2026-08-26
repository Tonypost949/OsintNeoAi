import re

file_path = r'C:\Users\Amd949609\.gemini\antigravity-cli\brain\e0259c57-0b03-45f8-956f-927ea22d1195\.system_generated\steps\6158\content.md'
with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Clean script & style
text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
text = re.sub(r'<style.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
text = re.sub(r'<[^>]+>', ' ', text)
lines = [l.strip() for l in text.splitlines() if l.strip()]

print("=== STATE OF CALIFORNIA HOUSING IS KEY (HOUSING.CA.GOV) ===")
for l in lines[:50]:
    print("->", l)
