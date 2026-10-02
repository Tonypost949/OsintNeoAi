import json
import subprocess

dossier_path = r"C:\EVIDENCE_LOCKER_MASTER\00_INDEX\UNIFIED_MASTER_INVESTIGATIVE_DOSSIER.md"
summary_path = r"C:\EVIDENCE_LOCKER_MASTER\20_ANALYSIS\EPA_PCS_CORRELATION_SUMMARY.json"

with open(summary_path, "r", encoding="utf-8") as f:
    summary = json.load(f)

hb_permits = summary.get("huntington_beach_permits", [])

lines = [
    "",
    "## 7. Official US EPA Water Discharge Permits (Huntington Beach NPDES)",
    "- **Total Ingested EPA Records:** 203,441",
    "- **California Permits:** 2,187",
    "- **Huntington Beach Permits Identified:** 9",
    "",
    "| NPDES Permit ID | Facility Name | Location Address | Receiving Waters | Status / Type |",
    "|---|---|---|---|---|"
]

for p in hb_permits:
    npdes = p.get("npdes", "N/A")
    name = p.get("name_1", "N/A")
    street = f"{p.get('location_street_1', '')} {p.get('location_street_2', '')}".strip()
    waters = p.get("receiving_waters", "N/A")
    ownership = p.get("type_of_ownership", "N/A")
    lines.append(f"| `{npdes}` | {name} | {street} | {waters} | {ownership} |")

with open(dossier_path, "a", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print("Successfully appended EPA NPDES permits to UNIFIED_MASTER_INVESTIGATIVE_DOSSIER.md")

# Mirror updated dossier to Google Drive
subprocess.run(["rclone", "copy", dossier_path, "gdrive:Sharedall/EVIDENCE_LOCKER_MASTER/00_INDEX", "-v"])
