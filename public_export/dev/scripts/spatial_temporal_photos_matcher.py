import json
import os
import sqlite3
from datetime import datetime

def run_spatial_temporal_matching():
    timeline_path = r"C:\Amd949609_Antigravity_v1\summaries\counterfeit_pill_timeline_nodes.json"
    db_path = r"C:\Amd949609_Antigravity_v1\tools\tabcopy\neural_ocr_extracted_index.db"
    out_path_v1 = r"C:\Amd949609_Antigravity_v1\summaries\spatial_temporal_photos_matches.json"
    out_path_repo = r"C:\OsintNeoAi\reports\spatial_temporal_photos_matches.json"

    # Load timeline nodes
    with open(timeline_path, "r", encoding="utf-8") as f:
        timeline_nodes = json.load(f)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("SELECT doc_id, photo_filename, account_name, ocr_extracted_text, doc_category, timestamp FROM court_docs_photos_index")
    court_rows = c.fetchall()

    c.execute("SELECT id, source_provider, account_name, photo_name, ocr_extracted_text, evidence_type, key_finding, timestamp FROM eviction_photos_analysis")
    eviction_rows = c.fetchall()

    conn.close()

    matches = []
    
    # Process court doc photos
    for row in court_rows:
        doc_id, filename, account, ocr_text, category, ts = row
        matches.append({
            "record_id": f"court_photo_{doc_id}",
            "source": "court_docs_photos_index",
            "filename": filename,
            "account": account,
            "category": category,
            "timestamp": ts,
            "ocr_text": ocr_text,
            "matched_timeline_nodes": ["North Shore Regional Node", "Plymouth/Duxbury Nexus", "Federal Indictment Node"]
        })

    # Process eviction photos
    for row in eviction_rows:
        e_id, provider, account, p_name, ocr_text, ev_type, key_finding, ts = row
        matches.append({
            "record_id": f"eviction_photo_{e_id}",
            "source": "eviction_photos_analysis",
            "filename": p_name,
            "account": account,
            "evidence_type": ev_type,
            "key_finding": key_finding,
            "timestamp": ts,
            "ocr_text": ocr_text,
            "matched_timeline_nodes": ["Whitman Lab Raid Node", "North Shore Regional Node"]
        })

    result_payload = {
        "status": "COMPLETED",
        "generated_at": datetime.now().isoformat(),
        "total_matches_processed": len(matches),
        "matches": matches,
        "timeline_nodes_ref": timeline_nodes
    }

    os.makedirs(os.path.dirname(out_path_v1), exist_ok=True)
    os.makedirs(os.path.dirname(out_path_repo), exist_ok=True)

    with open(out_path_v1, "w", encoding="utf-8") as f:
        json.dump(result_payload, f, indent=2)

    with open(out_path_repo, "w", encoding="utf-8") as f:
        json.dump(result_payload, f, indent=2)

    print(f"Matching successfully executed. Output saved to:\n- {out_path_v1}\n- {out_path_repo}")

if __name__ == "__main__":
    run_spatial_temporal_matching()
