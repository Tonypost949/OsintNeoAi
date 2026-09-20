import re

filepath = r"C:\Users\Amd949609\Downloads\Power Apps _ Apps.html"

with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

# Extract all text blocks between tags
clean_text = re.sub(r'<[^>]+>', ' ', content)
clean_text = ' '.join(clean_text.split())

print("=== RAW TEXT SNIPPETS FROM POWER APPS HTML ===")
keywords = ['bbbf5a84', 'OsintNeoAi', 'Source Manager', 'Studio', '584c706d', 'vibe', 'app']
for kw in keywords:
    matches = [m.start() for m in re.finditer(kw, clean_text, re.IGNORECASE)]
    print(f"\nKeyword '{kw}' matches count: {len(matches)}")
    for m in matches[:3]:
        snippet = clean_text[max(0, m-100):min(len(clean_text), m+200)]
        print(f"  Snippet: ... {snippet} ...")
