import os
import re
import json
from pathlib import Path

txt_file = Path(r'C:\OsintNeoAi\evidence\geotracker_17631_cameron_full_text.txt')
content = txt_file.read_text(encoding='utf-8', errors='ignore')

pages = content.split('--- PAGE ')

summary_pages = []
for p in pages:
    p_lower = p.lower()
    if any(k in p_lower for k in ['executive summary', 'site history', 'historical use', 'source area', 'underground storage tank', 'ust', 'pce', 'tce', 'tetrachloroethene', 'trichloroethene', 'benzene', 'plume', 'groundwater flow', 'soil vapor']):
        lines = p.splitlines()
        p_num = lines[0].split(' ---')[0] if lines else '?'
        summary_pages.append({
            'page': p_num,
            'text': "\n".join(lines[1:])
        })

print(f"=== SCIENTIFIC EVALUATION OF CONTAMINATION ORIGIN (17631 CAMERON LN) ===")
print(f"Total High-Priority Environmental Assessment Pages Analyzed: {len(summary_pages)}\n")

key_sections = []
for item in summary_pages[:15]:
    key_sections.append(f"### PAGE {item['page']}\n{item['text'][:1500]}\n")

out_summary = Path(r'C:\OsintNeoAi\evidence\geotracker_17631_cameron_scientific_summary.md')
out_summary.write_text("\n".join(key_sections), encoding='utf-8')
print(f"✓ Saved key scientific sections to: {out_summary}")
