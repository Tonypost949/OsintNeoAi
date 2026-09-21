import json
import os

def search_hospital_records():
    manifest_path = r"C:\OsintNeoAi\EVIDENCE_LOCKER_SHA256_MANIFEST.json"
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            hospital_files = []
            keywords = ["hospital", "er", "emergency", "admission", "discharge", "physician", "patient", "clinic", "treatment", "medical_report", "medical_record"]
            for item in data:
                item_str = json.dumps(item).lower()
                if any(k in item_str for k in keywords):
                    hospital_files.append(item)
            
            print(f"[+] Total Hospital & Clinical Discharge Records Found: {len(hospital_files)}")
            output_file = r"C:\OsintNeoAi\HOSPITAL_AND_CLINICAL_RECORDS_INDEX.json"
            with open(output_file, "w", encoding="utf-8") as out:
                json.dump(hospital_files, out, indent=2)
            print(f"[+] Index written to: {output_file}")

if __name__ == "__main__":
    search_hospital_records()
