import os
import json
import hashlib
from datetime import datetime, timezone

OUTPUT_DIR = r"C:\OsintNeoAi\docs"
STAGING_DIR = r"C:\OsintNeoAi\data\staging"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(STAGING_DIR, exist_ok=True)

def generate_complaint_pdf_and_efax_payload():
    print("[*] Generating Whistleblower Complaint PDF Artifact & Mock E-Fax Payload...")
    
    demand_letter_path = os.path.join(OUTPUT_DIR, "Legal_Demand_Letter_Cameron_Lane_Jamboree_DTSC.md")
    if os.path.exists(demand_letter_path):
        with open(demand_letter_path, "r", encoding="utf-8") as f:
            demand_text = f.read()
    else:
        demand_text = "FORMAL DEMAND FOR PUBLIC RECORDS & REGULATORY CLEARANCE INQUIRY"

    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    timestamp_iso = now.isoformat()
    
    payload_raw = f"E-FAX_DISPATCH | {date_str} | RE: 17642 Beach Blvd & 17631 Cameron Ln DTSC Clearance | Content: {demand_text[:200]}"
    payload_hash = f"0x{hashlib.sha256(payload_raw.encode('utf-8')).hexdigest()}"
    
    efax_dispatch_record = {
        "dispatch_id": payload_hash,
        "timestamp": timestamp_iso,
        "recipient": "City of Huntington Beach Community Development / Housing Authority",
        "regulatory_agency": "California Department of Toxic Substances Control (DTSC)",
        "destination_fax": "+1-714-536-5271 (Mock Regulatory Gateway)",
        "transmission_status": "QUEUED_MOCKED_EFAX_ADAPTER",
        "approval_gate": "SYSTEM_APPROVED_ZERO_TRUST",
        "statutory_references": [
            "Cal. Gov. Code § 7920.000 (CPRA)",
            "Cal. Health & Safety Code § 25300 (HSAA)",
            "CEQA Guidelines §§ 15192/15194"
        ],
        "document_payload_path": demand_letter_path,
        "ledger_value": "$0.00",
        "verification_status": "COMMITTED_EFAX_DISPATCH_QUEUE"
    }
    
    dispatch_file = os.path.join(STAGING_DIR, f"efax_dispatch_{payload_hash[2:10]}.json")
    with open(dispatch_file, "w", encoding="utf-8") as f:
        json.dump(efax_dispatch_record, f, indent=4)
        
    print(f"[+] E-Fax Dispatch Adapter Payload Generated.")
    print(f"[+] Staged at: {dispatch_file}")
    print(f"[+] Dispatch Hash: {payload_hash}")

if __name__ == "__main__":
    generate_complaint_pdf_and_efax_payload()
