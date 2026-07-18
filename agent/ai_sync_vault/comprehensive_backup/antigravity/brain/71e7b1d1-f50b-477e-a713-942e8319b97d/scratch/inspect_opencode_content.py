import os
import re

content_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\.system_generated\steps\5560\content.md"
output_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\opencode_inspection.txt"

with open(content_path, "r", encoding="utf-8") as f:
    text = f.read()

findings = []
findings.append(f"File size: {len(text)} characters")

# Find occurrences of file names
for ext in ["py", "html", "js", "sh", "json"]:
    matches = set(re.findall(r'([\w\-_\.]+\.' + ext + r')', text))
    findings.append(f"Files with extension .{ext} found ({len(matches)} unique): {list(matches)[:15]}")

# Let's search for mentions of "opencode_work" or "scrape_oc_procurement" or "load_procurement_to_bq"
for term in ["opencode_work", "scrape_oc_procurement.py", "load_procurement_to_bq.py", "index.html"]:
    matches = [m.start() for m in re.finditer(term, text)]
    findings.append(f"Term '{term}': {len(matches)} occurrences")
    for idx, pos in enumerate(matches[:5]):
        snippet = text[max(0, pos-200):min(len(text), pos+600)]
        findings.append(f"  Match {idx+1} at {pos}:\n{snippet}\n" + "-"*40)

with open(output_path, "w", encoding="utf-8") as out:
    out.write("\n".join(findings))

print("Inspection completed. Written to opencode_inspection.txt")
