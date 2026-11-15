with open("/mnt/c/Users/Amd949609/.gemini/antigravity-cli/brain/ea64803a-f47e-47f4-b552-f3a76584aedf/.system_generated/steps/900/content.md", "r", encoding="utf-8") as f:
    text = f.read()

import re
# Check for page title, sheet names, or data arrays
title_match = re.search(r'<meta property="og:title" content="([^"]+)"', text)
if title_match:
    print("Page Title:", title_match.group(1))

# Check for gviz or data chunks
for keyword in ["Summary of Outreach Efforts", "outreach", "Phase", "Verma", "Knabb"]:
    hits = [m.start() for m in re.finditer(re.escape(keyword), text, re.IGNORECASE)]
    print(f"Keyword '{keyword}': {len(hits)} hits")
    for pos in hits[:5]:
        snippet = text[max(0, pos-60):min(len(text), pos+120)]
        print("  Snippet:", repr(snippet))
