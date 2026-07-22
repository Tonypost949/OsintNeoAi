import os
import re

content_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\.system_generated\steps\5560\content.md"

with open(content_path, "r", encoding="utf-8") as f:
    text = f.read()

# Let's find "Index: opencode_work/scrape_oc_procurement.py"
pos = text.find("Index: opencode_work/scrape_oc_procurement.py")
if pos != -1:
    print(f"Found at position {pos}")
    # Let's print 1000 characters before and 3000 characters after
    snippet = text[max(0, pos-200):pos+3000]
    # To avoid terminal encoding errors, replace problematic characters or write to a file
    with open("scrape_patch_snippet.txt", "w", encoding="utf-8") as out:
        out.write(snippet)
    print("Snippet written to scrape_patch_snippet.txt")
else:
    print("Not found!")
