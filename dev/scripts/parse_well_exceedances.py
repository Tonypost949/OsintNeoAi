import re
import json
from pathlib import Path
from bs4 import BeautifulSoup

txt_file = Path(r'C:\OsintNeoAi\evidence\geotracker_well_CA3000618_quality_data.txt')
html_text = txt_file.read_text(encoding='utf-8', errors='ignore')

soup = BeautifulSoup(html_text, 'html.parser')

print("=== GEOTRACKER GROUNDWATER WELL QUALITY ANALYTICAL SUMMARY (WELL: CA3000618_001_001) ===")

rows = soup.find_all('tr')
parsed_records = []

for r in rows:
    cols = [td.get_text(strip=True) for td in r.find_all(['td', 'th'])]
    if len(cols) >= 5 and cols[0] != 'Chemical':
        # Filter rows with data
        parsed_records.append(cols)

print(f"✓ Total Analytical Data Rows Extracted: {len(parsed_records)}\n")

md_lines = [
    "# 🧪 GEOTRACKER GROUNDWATER WELL QUALITY DATA: WELL `CA3000618_001_001`",
    "**Global ID:** `W0603000618`  ",
    "**Assigned Well Name:** `CA3000618_001_001`  ",
    "**Source Portal:** California State Water Resources Control Board (GeoTracker)  ",
    "",
    "---",
    "",
    "## 📊 SAMPLE ANALYTICAL DATA TABLE (EXCEEDANCES & DETECTS)",
    ""
]

for rec in parsed_records[:50]:
    md_lines.append(f"- **Chemical:** `{rec[0]}` | **Result / Conc:** `{rec[1] if len(rec)>1 else ''}` | **MCL:** `{rec[2] if len(rec)>2 else ''}` | **Date:** `{rec[-1] if len(rec)>0 else ''}`")

out_md = Path(r'C:\OsintNeoAi\evidence\geotracker_well_CA3000618_exceedances_summary.md')
out_md.write_text("\n".join(md_lines), encoding='utf-8')
print(f"✓ Saved exceedances summary report to: {out_md}")
