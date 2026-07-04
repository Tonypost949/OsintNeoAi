import os
import sys

# Reconfigure stdout to use UTF-8 just in case
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

text_path = "./opencode_work/andrew_do_audit/phase1_forensic_audit_raw.txt"
with open(text_path, "r", encoding="utf-8") as f:
    text = f.read()

pages = text.split("--- PAGE ")
print(f"Total pages in text: {len(pages)}")

# 1. 360 Clinic Detailed Analysis
# Findings for 360 Clinic are typically on pages 30-40, let's extract them specifically.
clinic_pages = []
for p in pages:
    if not p:
        continue
    page_num = p.split(" ---")[0]
    p_lower = p.lower()
    try:
        page_int = int(page_num.strip())
        if 30 <= page_int <= 41:
            clinic_pages.append(p)
    except ValueError:
        pass

# 2. 2T Media Detailed Analysis
# Findings for 2T Media are typically on pages 13-26, let's extract them.
media_pages = []
for p in pages:
    if not p:
        continue
    page_num = p.split(" ---")[0]
    p_lower = p.lower()
    try:
        page_int = int(page_num.strip())
        if 13 <= page_int <= 27:
            media_pages.append(p)
    except ValueError:
        pass

output_dir = "./opencode_work/andrew_do_audit/"
findings_path = os.path.join(output_dir, "findings_summary.md")

with open(findings_path, "w", encoding="utf-8") as out:
    out.write("# Weaver Forensic Audit Phase 1 - Entity Extraction Findings\n\n")
    
    out.write("## 1. 360 Clinic Findings (Pages 30-41)\n\n")
    for cp in clinic_pages:
        out.write(f"### {cp.split(' ---')[0].strip()}\n")
        # Clean text from control characters/strange bullets
        cleaned = cp.replace('\uf0a7', '-').replace('\uf0b7', '-')
        out.write(cleaned + "\n\n")
        
    out.write("\n## 2. 2T Media Findings (Pages 13-27)\n\n")
    for mp in media_pages:
        out.write(f"### {mp.split(' ---')[0].strip()}\n")
        cleaned = mp.replace('\uf0a7', '-').replace('\uf0b7', '-')
        out.write(cleaned + "\n\n")

print(f"Saved extracted sections to {findings_path}")
