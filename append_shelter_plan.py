import subprocess

dossier_path = r"C:\EVIDENCE_LOCKER_MASTER\00_INDEX\UNIFIED_MASTER_INVESTIGATIVE_DOSSIER.md"

section = (
    "\n\n## 10. Official Huntington Beach Municipal Ingestion: Emergency Homeless Shelter Grading Plan\n"
    "- **Original Source File:** `C:\\Users\\Amd949609\\Downloads\\db66e1e0-b949-11f1-8e00-dbd4e67e7847.pdf`\n"
    "- **Master Locker File:** `C:\\EVIDENCE_LOCKER_MASTER\\20_ANALYSIS\\db66e1e0-b949-11f1-8e00-dbd4e67e7847.pdf`\n"
    "- **Extracted Text File:** `C:\\EVIDENCE_LOCKER_MASTER\\20_ANALYSIS\\db66e1e0-b949-11f1-8e00-dbd4e67e7847.pdf.txt`\n"
    "- **SHA256 Cryptographic Hash:** `5b4f0cd753c96c96fa41468db97001c8077e710d2c466644ac6a1d96e96109d6`\n"
    "- **Jurisdiction:** City of Huntington Beach Department of Public Works (714-536-5431)\n"
    "- **Project Title:** Precise Grading & Drainage Plan for Emergency Homeless Shelter\n"
    "- **Site Location:** 17631 Cameron Lane, Huntington Beach, CA\n"
    "- **Key Boundaries & Streets:** Warner Ave, Slater Ave, Newman Ave\n"
    "- **Regulatory Standards:** CAMUTCD 2014, WATCH 2019, City of Huntington Beach Standard Plan 100\n"
)

with open(dossier_path, "a", encoding="utf-8") as f:
    f.write(section)

print("Appended Emergency Homeless Shelter Grading Plan to UNIFIED_MASTER_INVESTIGATIVE_DOSSIER.md")

# Sync to Google Drive
subprocess.run(["rclone", "copy", dossier_path, "gdrive:Sharedall/EVIDENCE_LOCKER_MASTER/00_INDEX", "-v"])
print("Synced updated dossier to Google Drive.")
