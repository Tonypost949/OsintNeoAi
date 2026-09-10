#!/usr/bin/env python3
"""
TASK-074: AI Extraction Module for Dynamic Legal Precedent & Statutory Citation Indexing
Extracts statutes (e.g., CERCLA, RCRA, Cal Civil Code 1946.2, CCP 473(d), AB 1482)
from unorganized evidence text and maps them to structured JSON indices.
"""

import re
import json
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(ROOT_DIR, "data", "legal_precedents_and_statutes_index.json")

STATUTORY_PATTERNS = {
    "CERCLA_SUPERFUND": [r"42\s*U\.?S\.?C\.?\s*§?\s*9601", r"CERCLA", r"Superfund"],
    "RCRA_HAZARDOUS_WASTE": [r"42\s*U\.?S\.?C\.?\s*§?\s*6901", r"RCRA", r"cradle-to-grave"],
    "CAL_CIVIL_CODE_1946_2": [r"Civil\s*Code\s*§?\s*1946\.2", r"AB\s*1482", r"Tenant\s*Protection\s*Act"],
    "CAL_CCP_473_D": [r"Code\s*of\s*Civil\s*Procedure\s*§?\s*473\(d\)", r"CCP\s*473\(d\)", r"vacate\s*void\s*judgment"],
    "FED_RULE_60_D_3": [r"Rule\s*60\(d\)\(3\)", r"fraud\s*on\s*the\s*court"],
    "PORTER_COLOGNE_WATER_ACT": [r"Water\s*Code\s*§?\s*13000", r"Porter-Cologne"],
    "CAL_CORTESE_LIST": [r"Gov\.?\s*Code\s*§?\s*65962\.5", r"Cortese\s*List"],
    "NAGPRA_TRIBAL_BURIALS": [r"25\s*U\.?S\.?C\.?\s*§?\s*3001", r"NAGPRA", r"Pub\.?\s*Res\.?\s*Code\s*§?\s*5097\.94"]
}

def extract_statutes_from_text(text: str):
    matches = {}
    for key, patterns in STATUTORY_PATTERNS.items():
        for pattern in patterns:
            found = re.findall(pattern, text, re.IGNORECASE)
            if found:
                matches[key] = {
                    "matched_terms": list(set(found)),
                    "occurrence_count": len(found)
                }
                break
    return matches

def run_legal_indexing():
    print("[Legal Extractor] Scanning evidence and briefings directory...")
    evidence_dir = os.path.join(ROOT_DIR, "evidence")
    briefings_dir = os.path.join(ROOT_DIR, "briefings")
    
    indexed_documents = []
    
    for folder in [evidence_dir, briefings_dir]:
        if not os.path.exists(folder):
            continue
        for root, _, files in os.walk(folder):
            for file in files:
                if file.endswith((".md", ".txt", ".json")):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        statutes = extract_statutes_from_text(content)
                        if statutes:
                            indexed_documents.append({
                                "file": os.path.relpath(file_path, ROOT_DIR),
                                "detected_statutes": statutes
                            })
                    except Exception as e:
                        pass

    output_payload = {
        "generated_at": str(os.environ.get("DATE", "2026-09-10")),
        "total_files_indexed": len(indexed_documents),
        "documents": indexed_documents
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        json.dump(output_payload, out, indent=2)

    print(f"[Legal Extractor] Successfully indexed {len(indexed_documents)} documents with statutory anchors to {OUTPUT_FILE}")

if __name__ == "__main__":
    run_legal_indexing()
