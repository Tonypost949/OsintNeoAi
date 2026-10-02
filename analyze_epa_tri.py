import json
import subprocess

tri_path = r"C:\EVIDENCE_LOCKER_MASTER\20_ANALYSIS\OFFICIAL_GOV_APIS\EPA_TRI_FACILITIES.json"
summary_out = r"C:\EVIDENCE_LOCKER_MASTER\20_ANALYSIS\EPA_TRI_CORRELATION_SUMMARY.json"
dossier_path = r"C:\EVIDENCE_LOCKER_MASTER\00_INDEX\UNIFIED_MASTER_INVESTIGATIVE_DOSSIER.md"

with open(tri_path, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"TRI Data Type: {type(data)}")

if isinstance(data, list):
    records = data
elif isinstance(data, dict):
    records = data.get("TRI_FACILITIES", data.get("records", []))
else:
    records = []

summary = {
    "total_tri_facilities_ingested": len(records),
    "facilities_detail": records
}

with open(summary_out, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)

print(f"Ingested {len(records)} EPA TRI Facility records and saved to EPA_TRI_CORRELATION_SUMMARY.json")

# Append to Dossier
tri_section = [
    "",
    "## 8. Official US EPA Toxics Release Inventory (TRI) Facilities",
    f"- **Total Ingested TRI Facilities:** {len(records)}",
    "",
    "| TRI Facility ID | Facility Name | Address | City / State / Zip | Primary Industry / Chemicals |",
    "|---|---|---|---|---|"
]

for rec in records:
    if isinstance(rec, dict):
        tri_id = rec.get("tri_facility_id", rec.get("TRI_FACILITY_ID", "N/A"))
        name = rec.get("facility_name", rec.get("FACILITY_NAME", rec.get("name", "N/A")))
        address = rec.get("street_address", rec.get("STREET_ADDRESS", "N/A"))
        city = rec.get("city_name", rec.get("CITY_NAME", "Huntington Beach"))
        state = rec.get("state_abbr", rec.get("STATE_ABBR", "CA"))
        zip_code = rec.get("zip_code", rec.get("ZIP_CODE", "N/A"))
        industry = rec.get("primary_sic", rec.get("PRIMARY_SIC", rec.get("industry_sector", "N/A")))
        tri_section.append(f"| `{tri_id}` | {name} | {address} | {city}, {state} {zip_code} | {industry} |")

with open(dossier_path, "a", encoding="utf-8") as f:
    f.write("\n".join(tri_section) + "\n")

print("Appended TRI facilities to UNIFIED_MASTER_INVESTIGATIVE_DOSSIER.md")

# Mirror updated files to Google Drive
subprocess.run(["rclone", "copy", summary_out, "gdrive:Sharedall/EVIDENCE_LOCKER_MASTER/20_ANALYSIS", "-v"])
subprocess.run(["rclone", "copy", dossier_path, "gdrive:Sharedall/EVIDENCE_LOCKER_MASTER/00_INDEX", "-v"])

# Commit and Push
subprocess.run(["git", "add", "-A"], cwd=r"C:\OsintNeoAi")
subprocess.run(["git", "commit", "-m", "Analyze and ingest 27 EPA TRI Facility records into dossier"], cwd=r"C:\OsintNeoAi")
r_push = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True, cwd=r"C:\OsintNeoAi")
print("Git push status:", r_push.returncode, r_push.stdout, r_push.stderr)
