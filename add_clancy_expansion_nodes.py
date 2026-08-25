import json
import os

graph_paths = [
    r'C:\Users\Amd949609\OsintNeoAi-1\cli\data\graph.json',
    r'C:\Users\Amd949609\OsintNeoAi-1\cli\data\cases\nworico.json'
]

new_nodes = [
    {
        "id": "SDT_CLANCY_SUBPOENA_MATRIX",
        "name": "Subpoena Duces Tecum & Rule 26 Matrix (Clancy Evidence Lockers)",
        "type": "LegalPleading",
        "category": "EvidentiaryDemand",
        "jurisdiction": "Massachusetts / Federal District of Mass",
        "authorities": ["Mass. R. Crim. P. 17(c)", "Fed. R. Crim. P. 17(c)", "18 U.S.C. 1962"],
        "targets": ["Plymouth County DA", "MSP Crime Lab", "MGH Psychiatric Pharmacy", "DEA New England HIDTA"],
        "evidence_demanded": ["Raw GC-MS Data", "Pill Macrophotography", "DEA Form 7", "DSCSA Lot Tracking"]
    },
    {
        "id": "WHITMAN_LAB_CHEMICAL_CORRELATION",
        "name": "Whitman Counterfeit Pill Lab & Clancy Chemical Correlation Dossier",
        "type": "ForensicToxicology",
        "category": "ChemicalEvidence",
        "location": "122 Commercial St, Whitman, MA",
        "coordinates": [42.0809, -70.9334],
        "distance_to_scene": "14.8 miles (18 mins)",
        "suspect": "Andrew Billings",
        "chemicals": ["Bromazolam", "Clonazolam", "Flualprazolam", "Fentanyl", "Microcrystalline Cellulose"],
        "mechanism": "Acute Akathisia & Involuntary Triazolobenzodiazepine Intoxication"
    },
    {
        "id": "DR_ANN_VERMA_WHISTLEBLOWER_DOSSIER",
        "name": "Dr. Ann Verma Whistleblower Statement & Diagnostic Laundering Dossier",
        "type": "Whistleblower",
        "category": "PsychiatricGatekeeping",
        "whistleblower": "Dr. Ann Verma, M.D.",
        "statement_file": "DR_ANN_VERMA_RESCISSION_NOTICE.docx",
        "gatekeepers_exposed": ["Dr. Phillip Resnick (CWRU)", "Dr. Donald Kushon (Drexel)", "Dr. Avram Mack (Harvard)"],
        "pipelines_exposed": ["Pipeline 4: Diagnostic Laundering & Asset Stripping", "Medicaid Upcoding", "Title IV-E Removal"]
    }
]

new_edges = [
    {"source": "SDT_CLANCY_SUBPOENA_MATRIX", "target": "LINDSAY_CLANCY_RESIDENCE", "type": "TARGETS_SCENE_EVIDENCE"},
    {"source": "SDT_CLANCY_SUBPOENA_MATRIX", "target": "PLYMOUTH_COUNTY_DA", "type": "SUBPOENAS_EVIDENCE_LOCKER"},
    {"source": "WHITMAN_LAB_CHEMICAL_CORRELATION", "target": "WHITMAN_PILL_PRESS_LAB", "type": "ANALYZES_ILLICIT_OPERATION"},
    {"source": "WHITMAN_LAB_CHEMICAL_CORRELATION", "target": "LINDSAY_CLANCY_RESIDENCE", "type": "ESTABLISHES_TOXIC_PROXIMITY"},
    {"source": "DR_ANN_VERMA_WHISTLEBLOWER_DOSSIER", "target": "DR_PHILLIP_RESNICK", "type": "EXPOSES_GATEKEEPING"},
    {"source": "DR_ANN_VERMA_WHISTLEBLOWER_DOSSIER", "target": "DR_DONALD_KUSHON", "type": "EXPOSES_GATEKEEPING"},
    {"source": "DR_ANN_VERMA_WHISTLEBLOWER_DOSSIER", "target": "DR_AVRAM_MACK", "type": "EXPOSES_GATEKEEPING"}
]

for gp in graph_paths:
    if os.path.exists(gp):
        with open(gp, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        nodes = data.get('nodes', [])
        edges = data.get('edges', [])
        
        existing_ids = {n.get('id') for n in nodes}
        for nn in new_nodes:
            if nn['id'] not in existing_ids:
                nodes.append(nn)
                existing_ids.add(nn['id'])
                
        for ne in new_edges:
            if ne not in edges:
                edges.append(ne)
                
        data['nodes'] = nodes
        data['edges'] = edges
        
        with open(gp, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            
        print(f"[+] Updated {gp}: Total Nodes = {len(nodes)}, Total Edges = {len(edges)}")
