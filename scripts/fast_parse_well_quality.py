import re
from pathlib import Path

txt_path = Path(r'C:\OsintNeoAi\evidence\geotracker_well_CA3000618_quality_data.txt')
text = txt_path.read_text(encoding='utf-8', errors='ignore')

# Extract chemical names, links, and values
links = re.findall(r'<A HREF=\"well_plot3\.asp\?[^\"]+\">([^<]+)</A>', text)
print(f"=== GEOTRACKER WELL CA3000618_001_001 WATER QUALITY CHEMICAL LIST ===")
print(f"Total Chemical Test Parameter Links Extracted: {len(links)}\n")

unique_chemicals = list(set(links))
print(f"Total Unique Tested Analytes: {len(unique_chemicals)}")

out_md = Path(r'C:\OsintNeoAi\evidence\geotracker_well_CA3000618_chemical_list.md')
lines = [
    "# 🧪 GEOTRACKER GROUNDWATER WELL `CA3000618_001_001` TESTED ANALYTES LIST",
    "**Global ID:** `W0603000618`  ",
    "**Assigned Well Name:** `CA3000618_001_001`  ",
    f"**Total Tested Parameters:** {len(unique_chemicals)}",
    "",
    "---",
    "",
    "## 📋 EXTRACTED ANALYTES & CHEMICAL TARGETS",
    ""
]

for idx, chem in enumerate(sorted(unique_chemicals)):
    lines.append(f"{idx+1}. `{chem}`")

out_md.write_text("\n".join(lines), encoding='utf-8')
print(f"✓ Saved chemical list report to: {out_md}")
