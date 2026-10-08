import os
import json
import hashlib
from datetime import datetime, timezone

DOCS_DIR = r"C:\OsintNeoAi\docs"
STAGING_DIR = r"C:\OsintNeoAi\data\staging"

def build_f3_complaint_pdf_generator():
    print("[*] F3: Generating Deterministic Complaint PDF Payload...")
    
    demand_file = os.path.join(DOCS_DIR, "Legal_Demand_Letter_Cameron_Lane_Jamboree_DTSC.md")
    if os.path.exists(demand_file):
        with open(demand_file, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = "DTSC 7-Step Remedial Clearance Legal Demand"
        
    doc_hash = f"0x{hashlib.sha256(content.encode('utf-8')).hexdigest()}"
    
    pdf_artifact = {
        "artifact_id": f"PDF_COMPLAINT_{doc_hash[2:10]}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "document_type": "FORMAL_DTSC_LEGAL_DEMAND_PDF",
        "title": "Formal Demand for Public Records & DTSC Regulatory Clearance Status",
        "parcels": ["17642 Beach Blvd", "17631 Cameron Ln"],
        "content_hash": doc_hash,
        "sensitive_logging_disabled": True,
        "transmission_allowed": False
    }
    
    output_path = os.path.join(STAGING_DIR, f"complaint_pdf_artifact_{doc_hash[2:10]}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(pdf_artifact, f, indent=2)
        
    print(f"[+] F3 Complete: Complaint PDF artifact metadata generated at {output_path}")

if __name__ == "__main__":
    build_f3_complaint_pdf_generator()
