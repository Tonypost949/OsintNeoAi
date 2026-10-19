import csv
import os

artifacts_dir = r"C:\Users\HP\.gemini\antigravity\brain\2439d66c-6b54-42f6-9ce1-d7e4e6589ab9"
csv_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\forensic_master_spreadsheet.csv"
if not os.path.exists(csv_path):
    csv_path = os.path.join(artifacts_dir, "forensic_master_spreadsheet.csv")
    
ledger_path = os.path.join(artifacts_dir, "Makaveli_Task_Ledger.md")
out_path = os.path.join(artifacts_dir, "master_evidence_dossier.md")

# Ensure the CSV exists
if not os.path.exists(csv_path):
    print("CSV not found. Running generate_unified_dossier.py...")
    os.system(r'python "C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\generate_unified_dossier.py"')
    csv_path = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\forensic_master_spreadsheet.csv"

# Load Ledger
with open(ledger_path, 'r', encoding='utf-8') as f:
    ledger_content = f.read()

# Load CSV
cases = []
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        cases.append(row)

# Categorize cases
rico_cases = []
headway_cases = []
oc_gov_cases = []
national_coc_cases = []
other_cases = []

for c in cases:
    cat = c.get('Category', '')
    ent = c.get('Entity_Name', '')
    if 'Headway' in ent or 'Verma' in c.get('Individual_Name', ''):
        headway_cases.append(c)
    elif 'Conway' in ent or 'RICO' in cat or 'Money Laundering' in cat or 'Mercy House' in ent:
        rico_cases.append(c)
    elif 'City' in ent or 'Police' in ent or 'HBPD' in ent or 'Ascon' in ent or 'Huntington' in ent or 'SCE' in ent:
        oc_gov_cases.append(c)
    elif 'CoC' in ent or 'Balance of State' in ent:
        national_coc_cases.append(c)
    else:
        other_cases.append(c)

def format_case(c):
    return f"### {c['Case_ID']} ({c['Date']})\n- **Entity/Individual:** {c['Entity_Name']} - {c['Individual_Name']} ({c['Role_Title']})\n- **Category:** {c['Category']} / {c['Subcategory']}\n- **Incident:** {c['Incident_Description']}\n- **Legal Basis:** {c['Legal_Basis_Statute']}\n- **Notes:** {c['Notes']}\n- **Linked Cases:** {c['Linked_Case_IDs']}\n"

with open(out_path, 'w', encoding='utf-8') as f:
    f.write("# Master Evidence Dossier: The RICO / Headway / OC Government Nexus\n\n")
    f.write("This document provides a unified, consolidated view of all evidentiary findings across the Makaveli OSINT investigations. It directly addresses the request for 'all the evidence now' by mapping the investigation threads together.\n\n")
    
    f.write("## 1. Makaveli Task Ledger\n\n")
    f.write(ledger_content + "\n\n")
    
    f.write("---\n\n")
    f.write("## 2. Orange County RICO Apparatus (Conway Network & Mercy House)\n\n")
    for c in rico_cases:
        f.write(format_case(c) + "\n")
        
    f.write("## 3. Headway / TherapyMatch, Inc. (Whistleblower: Dr. Ann Verma)\n\n")
    for c in headway_cases:
        f.write(format_case(c) + "\n")
        
    f.write("## 4. Orange County Government & Infrastructure (Data Breaches, Environmental, Civil Rights)\n\n")
    for c in oc_gov_cases:
        f.write(format_case(c) + "\n")

    f.write("## 5. National CoC / HUD Vulnerability Nodes (Balance of State Scanning)\n\n")
    for c in national_coc_cases:
        f.write(format_case(c) + "\n")
        
    f.write("## 6. Other Linked Network Entities (FTX, Kroll, Foreign Intel)\n\n")
    for c in other_cases:
        f.write(format_case(c) + "\n")

print(f"Master Dossier created at {out_path}")
