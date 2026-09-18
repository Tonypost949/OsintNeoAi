import json
import os
import shutil
from datetime import datetime

def deposit_evidence():
    source_matches = r"C:\Amd949609_Antigravity_v1\summaries\spatial_temporal_photos_matches.json"
    target_locker_repo = r"C:\OsintNeoAi\evidence\ocr_transcripts_photos"
    target_locker_v1 = r"C:\Amd949609_Antigravity_v1\cloud_storage\evidence_locker\ocr_transcripts_photos"

    os.makedirs(target_locker_repo, exist_ok=True)
    os.makedirs(target_locker_v1, exist_ok=True)

    with open(source_matches, "r", encoding="utf-8") as f:
        data = json.load(f)

    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    manifest_repo = os.path.join(target_locker_repo, f"NEURAL_OCR_EVIDENCE_MANIFEST_{timestamp_str}.json")
    manifest_v1 = os.path.join(target_locker_v1, f"NEURAL_OCR_EVIDENCE_MANIFEST_{timestamp_str}.json")

    # Save manifest
    with open(manifest_repo, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    with open(manifest_v1, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # Save individual transcript files for each match
    for item in data.get("matches", []):
        rec_id = item["record_id"]
        filename = item.get("filename", "unknown.jpg")
        account = item.get("account", "unknown_account")
        ocr_text = item.get("ocr_text", "")
        
        individual_file = f"{rec_id}_{account.replace('@', '_at_')}.txt"
        
        file_path_repo = os.path.join(target_locker_repo, individual_file)
        file_path_v1 = os.path.join(target_locker_v1, individual_file)
        
        content = f"""=== OSINTNEOAI FORENSIC EVIDENCE RECORD ===
Record ID: {rec_id}
Source Table: {item.get('source')}
Filename: {filename}
Account: {account}
Category / Evidence Type: {item.get('category') or item.get('evidence_type')}
Timestamp: {item.get('timestamp')}
Key Finding: {item.get('key_finding', 'N/A')}
Matched Timeline Nodes: {', '.join(item.get('matched_timeline_nodes', []))}

--- OCR EXTRACTED TRANSCRIPT ---
{ocr_text}
"""
        with open(file_path_repo, "w", encoding="utf-8") as f:
            f.write(content)

        with open(file_path_v1, "w", encoding="utf-8") as f:
            f.write(content)

    print(f"Successfully deposited {len(data.get('matches', []))} evidence records to:\n- {target_locker_repo}\n- {target_locker_v1}")

if __name__ == "__main__":
    deposit_evidence()
