#!/usr/bin/env python3
"""
Mandatory Statutory Legal Mapping Engine for OsintNeoAi.
Rule: Any transaction, agreement, trade, cost, or physical/environmental risk MUST be mapped
to its exact governing Federal and State legal statutes.
"""

import sys
import json
from datetime import datetime

LEGAL_STATUTE_REGISTRY = {
    "FINANCIAL_COST_AND_CONTRACTS": [
        {
            "code": "Cal. Gov. Code § 1090",
            "title": "Prohibition Against Financial Interest in Public Contracts",
            "scope": "Applies to all public purchases, land deals, trade agreements, and vendor contracts."
        },
        {
            "code": "Cal. Gov. Code § 87100 (PRA)",
            "title": "Conflict of Interest & Form 700 Disclosure",
            "scope": "Mandates full disclosure of economic interests by public officials and land trusts."
        },
        {
            "code": "31 U.S.C. § 3729 (False Claims Act)",
            "title": "Federal Qui Tam & Public Waste Liability",
            "scope": "Applies to fraudulent billing or improper government contract expenditures."
        }
    ],
    "PHYSICAL_HARM_AND_ENVIRONMENTAL_RISK": [
        {
            "code": "Cal. Health & Safety Code § 25249.5 (Prop 65)",
            "title": "Toxic Chemical & Carcinogen Discharge Prohibition",
            "scope": "Applies to exposure to Hexavalent Chromium, lead, arsenic, and dangerous toxic dust."
        },
        {
            "code": "Cal. Pub. Res. Code § 21000 (CEQA)",
            "title": "California Environmental Quality Act Mandatory Review",
            "scope": "Mandates thorough environmental impact reports and long-term public health remediation."
        },
        {
            "code": "42 U.S.C. § 9601 (CERCLA / Superfund)",
            "title": "Comprehensive Environmental Response & Liability",
            "scope": "Strict liability for hazardous substance releases and improper environmental caps."
        }
    ],
    "DEALS_TRADES_AND_AGREEMENTS": [
        {
            "code": "Cal. Gov. Code § 54956.8 (Brown Act)",
            "title": "Real Property Negotiation Disclosure Mandate",
            "scope": "Governs closed-session real estate deals, requiring public reporting of final price and terms."
        },
        {
            "code": "Cal. Gov. Code § 6250 (CPRA / Public Records)",
            "title": "Mandatory Public Access to Government Contracts & Agreements",
            "scope": "Guarantees public right to inspect all agency trade agreements, leases, and warranties."
        }
    ]
}

def map_event_to_governing_statutes(event_type, description):
    print(f"[*] Mapping Event ({event_type}) to Governing Legal Statutes...")
    
    statute_matches = LEGAL_STATUTE_REGISTRY.get(event_type, [])
    
    mapping_record = {
        "event_description": description,
        "event_type": event_type,
        "governing_statutes_linked": statute_matches,
        "mandatory_repo_rule": "EVERY COST, DEAL, OR RISK MUST BE STATUTORILY LINKED TO LEGAL DATA IN LEGAL SECTION",
        "timestamp": datetime.now().isoformat()
    }

    print(f"[+] Successfully mapped {len(statute_matches)} legal statutes to event!")
    return mapping_record

if __name__ == "__main__":
    event_type = sys.argv[1] if len(sys.argv) > 1 else "FINANCIAL_COST_AND_CONTRACTS"
    desc = sys.argv[2] if len(sys.argv) > 2 else "17631 Cameron & 17642 Beach Blvd land purchase and 1-year asphalt cap contract."

    mapped = map_event_to_governing_statutes(event_type, desc)
    
    output_path = r"C:\OsintNeoAi\statutory_legal_mapping_registry.json"
    with open(output_path, "w") as f:
        json.dump(mapped, f, indent=2)
    print(f"[+] Legal mapping registry saved to: {output_path}")
    print(json.dumps(mapped["governing_statutes_linked"], indent=2))
