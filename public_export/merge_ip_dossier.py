import subprocess

dossier_path = r"C:\EVIDENCE_LOCKER_MASTER\00_INDEX\UNIFIED_MASTER_INVESTIGATIVE_DOSSIER.md"
ip_dossier_path = r"C:\EVIDENCE_LOCKER_MASTER\00_INDEX\PUBLIC_IPS_FORENSIC_SWEEP_DOSSIER.md"

with open(ip_dossier_path, "r", encoding="utf-8") as f:
    ip_content = f.read()

section = "\n\n## 9. Master Public IP Enrichment & Geolocation Sweep\n" + ip_content

with open(dossier_path, "a", encoding="utf-8") as f:
    f.write(section)

print("Appended IP Forensic Sweep to UNIFIED_MASTER_INVESTIGATIVE_DOSSIER.md")

# Mirror to Google Drive
subprocess.run(["rclone", "copy", dossier_path, "gdrive:Sharedall/EVIDENCE_LOCKER_MASTER/00_INDEX", "-v"])
print("Synced updated dossier to gdrive:Sharedall/EVIDENCE_LOCKER_MASTER/00_INDEX")
