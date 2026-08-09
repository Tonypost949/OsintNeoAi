import re

text_path = "./opencode_work/andrew_do_audit/phase1_forensic_audit_raw.txt"
with open(text_path, "r", encoding="utf-8") as f:
    text = f.read()

# We want to find sections discussing 360 Clinic and 2T Media.
# Let's extract pages or paragraphs where they appear.

pages = text.split("--- PAGE ")
print(f"Total pages: {len(pages)}")

clinic_pages = []
media_pages = []

for p in pages:
    if not p:
        continue
    page_num = p.split(" ---")[0]
    p_lower = p.lower()
    
    if "360 clinic" in p_lower:
        clinic_pages.append(page_num)
    if "2t media" in p_lower:
        media_pages.append(page_num)

print(f"360 Clinic found in {len(clinic_pages)} pages: {', '.join(clinic_pages[:20])}...")
print(f"2T Media found in {len(media_pages)} pages: {', '.join(media_pages[:20])}...")

# Let's extract some high-density mentions or interesting paragraphs
print("\n--- EXTRACTING KEY SECTIONS FOR 360 CLINIC ---")
clinic_paragraphs = []
for p in pages:
    if "360 clinic" in p.lower():
        # find sentences/paragraphs containing 360 clinic
        lines = p.split('\n')
        for line in lines:
            if "360 clinic" in line.lower() and len(line.strip()) > 30:
                clinic_paragraphs.append(line.strip())
                
print("\nSample 360 Clinic mentions:")
for cp in clinic_paragraphs[:15]:
    print(f"- {cp}")

print("\n--- EXTRACTING KEY SECTIONS FOR 2T MEDIA ---")
media_paragraphs = []
for p in pages:
    if "2t media" in p.lower():
        lines = p.split('\n')
        for line in lines:
            if "2t media" in line.lower() and len(line.strip()) > 30:
                media_paragraphs.append(line.strip())

print("\nSample 2T Media mentions:")
for mp in media_paragraphs[:15]:
    print(f"- {mp}")
