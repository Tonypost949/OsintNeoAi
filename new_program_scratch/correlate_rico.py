import os
import csv
import json
from datetime import datetime

# Define Paths
BASE_DIR = r"C:\Users\HP\OneDrive\Documents"
WORKSPACE_DIR = os.path.join(BASE_DIR, "AG2OSINTNEOMAXX")
SCRATCH_DIR = os.path.join(BASE_DIR, "new_program_scratch")
SPREADSHEET_PATH = os.path.join(WORKSPACE_DIR, "forensic_master_spreadsheet.csv")
OUTPUT_JSON = os.path.join(SCRATCH_DIR, "rico_multi_state_map.json")

def correlate_rico_network():
    print("[*] Initializing Aegis-RICO Multi-State Correlation Engine...")
    
    if not os.path.exists(SPREADSHEET_PATH):
        print(f"[-] Error: Master spreadsheet not found at {SPREADSHEET_PATH}")
        return
        
    # Create scratch folder if missing
    os.makedirs(SCRATCH_DIR, exist_ok=True)
    
    cases = []
    with open(SPREADSHEET_PATH, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("Case_ID"):
                cases.append(row)
                
    print(f"[*] Loaded {len(cases)} cases from master spreadsheet.")
    
    # Structural mappings
    network_nodes = {
        "enterprise_meta": {
            "name": "Orange County - Multi-State Continuum of Care (CoC) Financial Exploitation Enterprise",
            "statutes": [
                "18 U.S.C. § 1962 (RICO Conspiracy)",
                "18 U.S.C. § 1341 (Mail Fraud)",
                "18 U.S.C. § 1343 (Wire Fraud)",
                "18 U.S.C. § 1512 / 1519 (Obstruction of Justice / Alteration of Records)",
                "31 U.S.C. §§ 3729-3733 (False Claims Act)",
                "CA Govt Code § 87100 (Conflict of Interest)"
            ],
            "analysis_timestamp": datetime.now().isoformat()
        },
        "regional_nodes": {},
        "individuals": {},
        "entities": {}
    }
    
    for case in cases:
        case_id = case.get("Case_ID", "")
        cat = case.get("Category", "")
        subcat = case.get("Subcategory", "")
        entity = case.get("Entity_Name", "")
        indiv = case.get("Individual_Name", "")
        statute = case.get("Legal_Basis_Statute", "")
        desc = case.get("Incident_Description", "")
        juris = case.get("Jurisdiction", "")
        
        # Identify Multi-State Vulnerability Nodes (National Expansion)
        if cat == "National Expansion" or "Vulnerability Node" in subcat:
            node_name = entity if entity else desc.split(" ")[0]
            network_nodes["regional_nodes"][case_id] = {
                "type": "National Expansion Node",
                "location": node_name,
                "description": desc,
                "regulatory_gap": "Sheriff-only policing / No registered clinical social work billing (NPI vacuum)",
                "environmental_hazard": "EPA toxic overlays / heavy agricultural/industrial runoff",
                "statutory_violation": statute if statute else "False Claims Act / HUD ESG Requirements",
                "jurisdiction": juris
            }
            
        # Identify Board Self-Dealing Matrix (CA Regional Hub)
        elif cat == "Self-Dealing" or "Kickback" in subcat or entity == "Mercy House Board of Directors" or "Mercy House" in entity:
            if indiv and indiv != "Unknown" and indiv != "Multiple":
                network_nodes["individuals"][indiv] = {
                    "role": case.get("Role_Title", ""),
                    "entity": entity,
                    "incident": desc,
                    "statutes": statute,
                    "linked_cases": case.get("Linked_Case_IDs", "")
                }
            if entity and entity != "Unknown":
                network_nodes["entities"][entity] = {
                    "type": "Non-Profit Operating Entity / Board Link",
                    "description": desc,
                    "implicated_statutes": statute,
                    "linked_cases": case.get("Linked_Case_IDs", "")
                }
                
        # Identify Daneshrad "Property Shuffle" (CA/Anaheim Hub)
        elif "Daneshrad" in desc or "Daneshrad" in indiv or "Starpoint Properties" in entity:
            network_nodes["entities"]["Starpoint Properties LLC"] = {
                "type": "Private Real Estate Conduit",
                "control_individual": "Paul Daneshrad",
                "mechanism": "Circular Lease Tax Evasion / Rapid property shuffle using shell trusts",
                "implicated_statutes": statute if statute else "18 U.S.C. § 1341 & § 1343",
                "linked_cases": "CASE-044, CASE-045, CASE-046"
            }
            if indiv == "Paul Daneshrad" or "Daneshrad" in indiv:
                network_nodes["individuals"]["Paul Daneshrad"] = {
                    "role": "Board Trustee / Starpoint CEO",
                    "entity": "Starpoint Properties / Covenant House CA",
                    "incident": desc,
                    "statutes": statute
                }

    # Save to disk
    with open(OUTPUT_JSON, "w", encoding="utf-8") as out:
        json.dump(network_nodes, out, indent=4)
        
    print(f"[+] Successfully generated Multi-State RICO mapping JSON at: {OUTPUT_JSON}")
    print(f" -> Mapped {len(network_nodes['regional_nodes'])} National CoC Vulnerability Nodes.")
    print(f" -> Mapped {len(network_nodes['individuals'])} Key High-Value Implicated Targets.")
    print(f" -> Mapped {len(network_nodes['entities'])} Enterprise Conduit Entities.")

if __name__ == "__main__":
    correlate_rico_network()
