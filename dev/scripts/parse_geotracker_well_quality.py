import re
import json
from pathlib import Path

content_file = Path(r'C:\Users\Amd949609\.gemini\antigravity-cli\brain\e616d655-4be6-4f57-bfad-24249ce3f54e\.system_generated\steps\1443\content.md')

if content_file.exists():
    text = content_file.read_text(encoding='utf-8', errors='ignore')
    
    # Extract table rows or analytical matches
    lines = text.splitlines()
    print(f"=== GEOTRACKER WELL QUALITY ANALYTICAL PARSER (WELL: CA3000618_001_001) ===")
    print(f"Total Page Content Lines: {len(lines)}\n")

    chemical_data = []
    for line in lines:
        if any(term in line.lower() for term in ['mg/l', 'ug/l', 'µg/l', 'mcl', 'pce', 'tce', 'benzene', 'chromium', 'nitrate', 'lead', 'arsenic', 'perchlorate', 'pfas', 'pfos', 'voc', 'chemical']):
            chemical_data.append(line.strip())

    out_file = Path(r'C:\OsintNeoAi\evidence\geotracker_well_CA3000618_quality_data.txt')
    out_file.write_text("\n".join(lines), encoding='utf-8')
    print(f"✓ Saved full well quality report text to: {out_file}")
    
    print("\nSample Chemical & Analytical Data Extracted:")
    for d in chemical_data[:20]:
        print(f"  - {d[:120]}")
else:
    print(f"File not found: {content_file}")
