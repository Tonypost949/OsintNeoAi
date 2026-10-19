import re
from pathlib import Path
from bs4 import BeautifulSoup

txt_path = Path(r'C:\OsintNeoAi\evidence\geotracker_well_CA3000618_quality_data.txt')
text = txt_path.read_text(encoding='utf-8', errors='ignore')

soup = BeautifulSoup(text, 'html.parser')
table = soup.find('table', {'id': 'mytbl'})

records = []

if table:
    rows = table.find_all('tr')
    print(f"=== PARSING GEOTRACKER WELL CA3000618_001_001 ({len(rows)} ROWS) ===")
    
    for r in rows:
        tds = r.find_all('td')
        if len(tds) >= 6:
            date = tds[0].get_text(strip=True)
            param = tds[1].get_text(strip=True)
            qualifier = tds[2].get_text(strip=True)
            result = tds[3].get_text(strip=True)
            units = tds[4].get_text(strip=True)
            mcl = tds[5].get_text(strip=True)
            
            if date != 'DATE' and param != 'PARAMETER':
                records.append({
                    'date': date,
                    'param': param,
                    'qualifier': qualifier,
                    'result': result,
                    'units': units,
                    'mcl': mcl
                })

print(f"✓ Total Extracted Water Quality Sampling Records: {len(records)}\n")

md_lines = [
    "# 🧪 GEOTRACKER GROUNDWATER WELL QUALITY AUDIT REPORT: WELL `CA3000618_001_001`",
    "**Global ID:** `W0603000618`  ",
    "**Assigned Well Name:** `CA3000618_001_001`  ",
    "**Source Portal:** California State Water Resources Control Board (GeoTracker)  ",
    f"**Total Historical Sampling Records Analyzed:** {len(records)}",
    "",
    "---",
    "",
    "## 📊 VERBATIM WATER QUALITY SAMPLING RECORDS (SAMPLE EXTRACT)",
    "",
    "| Sampling Date | Tested Parameter / Chemical | Qualifier | Result | Units | State MCL |",
    "| :--- | :--- | :--- | :--- | :--- | :--- |"
]

for rec in records[:100]:
    md_lines.append(f"| {rec['date']} | **{rec['param']}** | `{rec['qualifier']}` | **{rec['result']}** | {rec['units']} | {rec['mcl']} |")

out_md = Path(r'C:\OsintNeoAi\evidence\geotracker_well_CA3000618_parsed_records.md')
out_md.write_text("\n".join(md_lines), encoding='utf-8')
print(f"✓ Saved parsed records report to: {out_md}")
