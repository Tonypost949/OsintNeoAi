import json
import os

def check_medical_records():
    manifest_path = r"C:\OsintNeoAi\EVIDENCE_LOCKER_SHA256_MANIFEST.json"
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            med_files = []
            keywords = ["med", "health", "eurofins", "toxic", "blood", "doctor", "hospital", "clinical", "analytical", "dossier", "exposure", "contaminant"]
            for item in data:
                item_str = json.dumps(item).lower()
                if any(k in item_str for k in keywords):
                    med_files.append(item)
            
            print(f"[+] Total Medical, Toxicological & Analytical Health Files Found: {len(med_files)}")
            output_file = r"C:\OsintNeoAi\MEDICAL_AND_HEALTH_EVIDENCE_INDEX.json"
            with open(output_file, "w", encoding="utf-8") as out:
                json.dump(med_files, out, indent=2)
            print(f"[+] Index written to: {output_file}")

if __name__ == "__main__":
    check_medical_records()
