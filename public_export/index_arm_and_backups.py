import json
import os

def index_all_system_backups_and_arm_injury():
    print("[+] AUDITING ALL PC BACKUPS, GOOGLE PHOTOS, PHONE LOGS & ARM INJURY RECORDS...")
    
    manifest_path = r"C:\OsintNeoAi\EVIDENCE_LOCKER_SHA256_MANIFEST.json"
    arm_injury_records = []
    phone_backup_records = []
    cloud_storage_records = []
    
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
            for item in data:
                item_str = json.dumps(item).lower()
                
                # Check Arm Injury & Physical Medical Evidence
                if any(k in item_str for k in ["arm", "injury", "fracture", "wound", "trauma", "er_", "hospital", "doctor", "photo_"]):
                    arm_injury_records.append(item)
                    
                # Check Phone Backups & Call/SMS Logs
                if any(k in item_str for k in ["phone", "backup", "sms", "call", "contacts", "vcf", "chat", "takeout", "tmobile"]):
                    phone_backup_records.append(item)
                    
                # Check Cloud Storage & Account Syncs
                if any(k in item_str for k in ["google_drive", "google_photos", "onedrive", "gdrive", "photos", "cloud"]):
                    cloud_storage_records.append(item)
                    
    results = {
        "arm_injury_and_medical_photos": {
            "count": len(arm_injury_records),
            "samples": arm_injury_records[:10]
        },
        "phone_backups_and_communication_logs": {
            "count": len(phone_backup_records),
            "samples": phone_backup_records[:10]
        },
        "cloud_storage_and_account_mirrors": {
            "count": len(cloud_storage_records),
            "samples": cloud_storage_records[:10]
        }
    }
    
    out_file = r"C:\OsintNeoAi\SYSTEM_WIDE_BACKUPS_AND_ARM_INJURY_INDEX.json"
    with open(out_file, "w", encoding="utf-8") as out:
        json.dump(results, out, indent=2)
        
    print(f"[+] Audit complete. Arm Injury Records: {len(arm_injury_records)} | Phone Backups: {len(phone_backup_records)} | Cloud Records: {len(cloud_storage_records)}")
    print(f"[+] Output written to: {out_file}")

if __name__ == "__main__":
    index_all_system_backups_and_arm_injury()
