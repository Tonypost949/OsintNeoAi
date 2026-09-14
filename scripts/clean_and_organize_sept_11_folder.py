import os
import shutil
import json

base = r"C:\OsintNeoAi\data\takeouts\etp949609_takeout_20260913"
sept11_dir = os.path.join(base, "sept_11_phone_theft_investigation")
data_dir = os.path.join(base, "data")
data_meta_dir = os.path.join(data_dir, "metadata")

os.makedirs(sept11_dir, exist_ok=True)
os.makedirs(data_dir, exist_ok=True)
os.makedirs(data_meta_dir, exist_ok=True)

# 1. Move all historical / non-2026 files from sept_11 folder to data/
historical_files = [
    "2016_SEPTEMBER.json", "2017_SEPTEMBER.json", "2018_SEPTEMBER.json",
    "2022_SEPTEMBER.json", "2023_SEPTEMBER.json", "Installs.json",
    "Library.json", "Order History.json", "Purchase History.json",
    "All mail Including Spam and Trash.mbox"
]

print("[CLEANUP] Moving historical and general data files from sept_11 to data/...")
for hf in historical_files:
    src = os.path.join(sept11_dir, hf)
    dest = os.path.join(data_dir, hf)
    if os.path.exists(src):
        shutil.move(src, dest)
        print(f"  -> Moved {hf} to data/")
        
        # Create metadata index in data/metadata/
        meta_dest = os.path.join(data_meta_dir, hf + ".meta.json")
        try:
            st = os.stat(dest)
            with open(meta_dest, "w", encoding="utf-8") as mfp:
                json.dump({
                    "filename": hf,
                    "target_location": "data/",
                    "size_bytes": st.st_size,
                    "type": "HISTORICAL_ARCHIVE"
                }, mfp, indent=2)
        except Exception:
            pass

# 2. Build dedicated September 11, 2026 Phone Theft Incident Files
incident_report = """# SEPTEMBER 11, 2026 — PHONE LOSS / THEFT FORENSIC DOSSIER

**Target Identity**: `etp949609@gmail.com`  
**Incident Date**: September 11, 2026  
**Registered Devices**:
- Model `U616AT` (AT&T Motivate)
- Model `Stratus_C7` (Tracfone / Along Mobile `ms-android-tracfone-us-rvc3`)
- Model `motorola one 5G UW ace`

---

## 1. Incident Overview & Sequence
- **Primary Account**: `etp949609@gmail.com`
- **Known Activity Hotspots (Orange County)**:
  - Huntington Beach (80 Huntington St, Seaside Village, Beach Blvd)
  - Costa Mesa (Harbor Blvd, Newport Blvd)
  - Westminster (Goldenwest St, Chinook Ave)

---

## 2. Investigation Action Vectors
1. **Device Ping Disconnect**: Logging final Google Play Services check-in on Sept 11, 2026.
2. **Security & SIM Changes**: Monitoring carrier SIM-swap alerts, password resets, and unauthorized sign-in attempts.
3. **Recovery & Communication Logs**: Extracting incoming SMS, 2FA prompts, and Google Voice messages from Sept 11, 2026.
"""

with open(os.path.join(sept11_dir, "SEPT_11_2026_PHONE_THEFT_INCIDENT_REPORT.md"), "w", encoding="utf-8") as fp:
    fp.write(incident_report)

incident_data = {
    "target_account": "etp949609@gmail.com",
    "incident_date": "2026-09-11",
    "focus": "Phone Theft / Loss Reconstruction",
    "investigation_status": "ISOLATED_FORENSIC_VECTOR",
    "isolated_evidence_folder": "C:/OsintNeoAi/data/takeouts/etp949609_takeout_20260913/sept_11_phone_theft_investigation/"
}

with open(os.path.join(sept11_dir, "SEPT_11_2026_INCIDENT_DOSSIER.json"), "w", encoding="utf-8") as fp:
    json.dump(incident_data, fp, indent=2)

print("[✓] sept_11_phone_theft_investigation cleaned and isolated strictly for Sept 11, 2026 phone incident.")
