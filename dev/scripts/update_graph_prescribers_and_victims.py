import json

p_graph = r'C:\Users\Amd949609\OsintNeoAi-1\cli\data\graph.json'
p_case = r'C:\Users\Amd949609\OsintNeoAi-1\cli\data\cases\nworico.json'

new_nodes = [
    {
        'id': 'dr_jennifer_tufts',
        'label': 'Dr. Jennifer Tufts',
        'type': 'Physician_Prescriber',
        'properties': {
            'role': 'Outpatient Psychiatrist for Lindsay Clancy',
            'prescribed': ['Sertraline 25mg', 'Ativan 0.5/1mg', 'Hydroxyzine 25mg', 'Buspirone', 'Lamictal', 'Valium', 'Amitriptyline 10-20mg'],
            'dates': 'Sept 15, 2022 - Jan 23, 2023',
            'jurisdiction': 'Massachusetts',
            'liability': 'Mass. Gen. Laws ch. 231 s. 60B Malpractice & Polypharmacy'
        }
    },
    {
        'id': 'np_julie_paul',
        'label': 'NP Julie Paul',
        'type': 'Nurse_Practitioner_Prescriber',
        'properties': {
            'role': 'Prescriber responsible for Nov 25, 2022 Quadruple-Stack',
            'prescribed': ['Prozac 10mg', 'Klonopin', 'Ambien', 'Remeron'],
            'dates': 'Nov 21 - Nov 25, 2022',
            'jurisdiction': 'Massachusetts',
            'liability': 'Extreme Polypharmacy Stacking Breach of Standard of Care'
        }
    },
    {
        'id': 'rebecca_jollotta',
        'label': 'Rebecca Jollotta',
        'type': 'Clinical_Prescriber',
        'properties': {
            'role': 'Prescriber responsible for Seroquel 400mg Escalation',
            'prescribed': ['Seroquel 400mg/day', 'Valium'],
            'dates': 'Nov 29 - Dec 6, 2022',
            'jurisdiction': 'Massachusetts',
            'liability': 'Massive D2 Dopamine Blockade & Iatrogenic Akathisia Induction'
        }
    },
    {
        'id': 'peach_goldenberg',
        'label': 'Peach Goldenberg (Fatal Victim)',
        'type': 'Victim_Fatal_Counterfeit',
        'properties': {
            'age': 57,
            'location': 'South Hadley, MA',
            'cause': 'Fatal ingestion of counterfeit Oxycodone containing Metonitazene',
            'chemical': 'Metonitazene (Synthetic Nitazene Opioid)'
        }
    },
    {
        'id': 'clifton_dubois',
        'label': 'Clifton Dubois (Fatal Victim)',
        'type': 'Victim_Fatal_Counterfeit',
        'properties': {
            'age': 19,
            'year': 2021,
            'location': 'Rhode Island / MA border corridor',
            'cause': 'Fatal counterfeit pill overdose'
        }
    },
    {
        'id': 'lynn_counterfeit_ring',
        'label': 'Lynn Counterfeit Pill Enterprise',
        'type': 'Illicit_Manufacturing_Ring',
        'properties': {
            'operators': ['Daniel Blaney', 'Kenneth Lora', 'David Kable Jr.', 'Javier Bermudez'],
            'fatalities': 'At least 12 confirmed fatal overdoses',
            'chemicals': ['Fentanyl', 'Methamphetamine', 'Pyro (N-Pyrrolidino-Etonitazene 20-40x Fentanyl)'],
            'products': ['Fake Oxy M30', 'Fake Xanax GG249', 'Fake Adderall 30mg']
        }
    }
]

new_edges = [
    {'source': 'dr_jennifer_tufts', 'target': 'lindsay_clancy', 'label': 'PRESCRIBED_POLYPHARMACY', 'type': 'MEDICAL_MALPRACTICE'},
    {'source': 'np_julie_paul', 'target': 'lindsay_clancy', 'label': 'QUADRUPLE_STACK_PRESCRIBER', 'type': 'MEDICAL_MALPRACTICE'},
    {'source': 'rebecca_jollotta', 'target': 'lindsay_clancy', 'label': 'SEROQUEL_400MG_ESCALATION', 'type': 'MEDICAL_MALPRACTICE'},
    {'source': 'lynn_counterfeit_ring', 'target': 'peach_goldenberg', 'label': 'REGIONAL_SYNTHETIC_OPIOID_NEXUS', 'type': 'COUNTERFEIT_ENTERPRISE'},
    {'source': 'whitman_pill_lab', 'target': 'lynn_counterfeit_ring', 'label': 'REGIONAL_ROTARY_PRESS_NETWORK', 'type': 'ILLICIT_SUPPLY_CHAIN'}
]

for p in [p_graph, p_case]:
    with open(p, 'r', encoding='utf-8') as f:
        d = json.load(f)
    existing_ids = {n['id'] for n in d.get('nodes', [])}
    for n in new_nodes:
        if n['id'] not in existing_ids:
            d['nodes'].append(n)
            existing_ids.add(n['id'])
    d['edges'].extend(new_edges)
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(d, f, indent=2)
    print(f"[+] Updated {p}: Total Nodes: {len(d['nodes'])}, Total Edges: {len(d['edges'])}")
