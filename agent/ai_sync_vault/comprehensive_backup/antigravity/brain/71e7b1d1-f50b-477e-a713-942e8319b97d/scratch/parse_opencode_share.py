import os
import json
import re

content_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\.system_generated\steps\5560\content.md"

with open(content_path, "r", encoding="utf-8") as f:
    text = f.read()

# Let's find any occurrences of $R[...]=
print(f"File size: {len(text)} characters")

# Find if there are specific JSON objects or messages
# Let's search for "content" or "user_prompt" or similar
matches_content = re.findall(r'"content":\s*"([^"]+)"', text)
print(f"Found {len(matches_content)} content fields.")

# Let's look for markdown blocks or files in the text
matches_files = re.findall(r'(\w+_\w+\.(?:py|html|sh|js))', text)
print(f"Unique files mentioned: {set(matches_files)}")

# Let's print out some snippets where there are python scripts or messages
# Let's look for text indicating things like S3 URLs, scrape, OCR, or geocode
keywords = ["S3", "OCR", "geocode", "procurement", "national", "Philippines", "remittance"]
for kw in keywords:
    matches = [m.start() for m in re.finditer(kw, text, re.IGNORECASE)]
    print(f"Keyword '{kw}': {len(matches)} occurrences")
    for idx, pos in enumerate(matches[:3]):
        snippet = text[max(0, pos-100):min(len(text), pos+300)]
        print(f"  [{idx+1}] ...{snippet}...\n")
