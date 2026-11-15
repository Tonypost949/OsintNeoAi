import pypdf
import os
import re

pdf_path = r"C:\Amd949609_Antigravity_v1\evidence\truthfinder_records\TruthFinder_Dale_Ann_Verma_Extended_View.pdf"

if not os.path.exists(pdf_path):
    print("PDF not found!")
    exit(1)

reader = pypdf.PdfReader(pdf_path)
print(f"Total Pages in Extended View PDF: {len(reader.pages)}")

found_mentions = []
for idx, page in enumerate(reader.pages):
    text = page.extract_text() or ""
    # Look for trust, estate, deed, property, asset keywords
    keywords = ["trust", "estate", "deed", "probate", "grantor", "grantee", "property", "asset", "holding"]
    for kw in keywords:
        matches = re.finditer(re.escape(kw), text, re.IGNORECASE)
        for m in matches:
            start = max(0, m.start() - 150)
            end = min(len(text), m.end() + 150)
            snippet = text[start:end].replace("\n", " ").strip()
            found_mentions.append({
                "page": idx + 1,
                "keyword": kw,
                "snippet": snippet
            })

print(f"Total keyword matches: {len(found_mentions)}")
import json
with open(r"C:\Amd949609_Antigravity_v1\evidence\network_sessions\extended_pdf_trust_audit.json", "w", encoding="utf-8") as f:
    json.dump(found_mentions, f, indent=2)

# Print first 15 unique snippets
seen = set()
for m in found_mentions:
    clean = m["snippet"][:80]
    if clean not in seen:
        seen.add(clean)
        print(f"Page {m['page']} [{m['keyword']}]: {m['snippet']}\n---")
