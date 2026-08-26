import re

file_path = r'C:\Users\Amd949609\.gemini\antigravity-cli\brain\e0259c57-0b03-45f8-956f-927ea22d1195\.system_generated\steps\6123\content.md'
with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Strip scripts and styles
text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
text = re.sub(r'<style.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
text = re.sub(r'<[^>]+>', ' ', text)
lines = [l.strip() for l in text.splitlines() if l.strip()]

print("=== OC COURTS UNLAWFUL DETAINER RULES & FORMS ===")
for l in lines:
    if any(k in l.lower() for k in ['unlawful', 'detainer', 'eviction', 'writ', 'possession', 'sheriff', 'notice', 'form', 'stay', 'default', 'clerk', 'hearing', 'trial']):
        print("->", l)
