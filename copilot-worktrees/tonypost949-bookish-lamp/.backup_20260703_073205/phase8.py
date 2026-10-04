import json
from collections import defaultdict

with open(r'C:\Users\HP\OneDrive\Documents\AG2OSINTNEOMAXX\nodes.json') as f:
    nodes = json.load(f)
with open(r'C:\Users\HP\OneDrive\Documents\AG2OSINTNEOMAXX\edges.json') as f:
    edges = json.load(f)

nm = {n['id']: n for n in nodes}

def ntype(n):
    return n.get('label', n.get('type'))

def props(n):
    return n.get('properties', {})

TARGETS = ['BELAVITA LLC', 'BELINGER LLC', 'MESAVILLE HOLDINGS LLC']
TARGET_IDS = [f'ORG_{t}' for t in TARGETS]
# Also try raw names since some nodes use names directly as IDs
TARGET_IDS += TARGETS

# Find the actual node IDs
target_nodes = {}
for nid, n in nm.items():
    p = props(n)
    name = p.get('name', '').strip().upper()
    if name in [t.upper() for t in TARGETS]:
        target_nodes[nid] = n

print('=== TARGET ENTITIES ===')
for nid, n in target_nodes.items():
    p = props(n)
    print(f'  Node ID: {nid}')
    print(f'  Name: {p.get("name", "N/A")}')
    print(f'  Business Type: {p.get("business_type", "N/A")}')
    print(f'  Status: {p.get("status", "N/A")}')
    print(f'  Risk Score: {p.get("risk_score", "N/A")}')
    print(f'  Flagged Reason: {p.get("flagged_reason", "N/A")}')
    print(f'  Formation Reason: {p.get("formation_reason", "N/A")}')
    print(f'  Source: {p.get("source_of_info", "N/A")}')
    print()

# Find edges involving target entities
print('=== OFFICERS, MANAGERS, REGISTERED AGENTS ===')
persons_found = {}  # person_id -> list of (org_name, role)
for e in edges:
    for tid in target_nodes:
        if e.get('source_id') == tid or e.get('target_id') == tid:
            if e['type'] in ('OFFICER_OF', 'DIRECTOR_OF', 'CONNECTED_TO'):
                # person -> org
                if e.get('source_id') == tid:
                    # org is source, person is target
                    pid = e.get('target_id')
                    s = nm.get(tid)
                    t = nm.get(pid)
                else:
                    pid = e.get('source_id')
                    s = nm.get(pid)
                    t = nm.get(tid)
                
                if s and t:
                    src_name = props(s).get('name', s['id'])
                    tgt_name = props(t).get('name', t['id'])
                    role = e.get('properties', {}).get('title', e.get('properties', {}).get('role', e['type']))
                    
                    if ntype(s) == 'PERSON':
                        persons_found.setdefault(s['id'], []).append((tgt_name, role, e['type']))
                    elif ntype(t) == 'PERSON':
                        persons_found.setdefault(t['id'], []).append((src_name, role, e['type']))

for pid, rels in sorted(persons_found.items(), key=lambda x: -len(x[1])):
    n = nm[pid]
    p = props(n)
    name = p.get('name', pid)
    role_type = p.get('role', 'PERSON')
    print(f'  {name} [{role_type}]')
    for org_name, role, etype in rels:
        print(f'    {etype}: {role} of {org_name}')
    print()

# Search wider graph for other orgs controlled by same individuals
print('=== OTHER ORGANIZATIONS CONTROLLED BY SAME INDIVIDUALS ===')
person_ids = list(persons_found.keys())
other_orgs = defaultdict(list)  # person_id -> [(org_name, role)]
for e in edges:
    if e['type'] in ('OFFICER_OF', 'DIRECTOR_OF', 'CONNECTED_TO', 'OWNS'):
        src = e.get('source_id')
        tgt = e.get('target_id')
        
        # Check person in either role
        person_in_edge = None
        other_org_id = None
        if src in person_ids:
            person_in_edge = src
            other_org_id = tgt
        elif tgt in person_ids:
            person_in_edge = tgt
            other_org_id = src
        
        if person_in_edge and other_org_id:
            on = nm.get(other_org_id)
            pn = nm.get(person_in_edge)
            if on and pn:
                oname = props(on).get('name', on['id'])
                pname = props(pn).get('name', pn['id'])
                
                # Skip if it's one of the original 3 targets
                if oname.upper() in [t.upper() for t in TARGETS]:
                    continue
                
                if ntype(on) == 'ORGANIZATION':
                    role = e.get('properties', {}).get('title', e.get('properties', {}).get('role', e['type']))
                    other_orgs[person_in_edge].append((oname, e['type'], role))

for pid, orgs in sorted(other_orgs.items(), key=lambda x: -len(x[1])):
    n = nm[pid]
    pname = props(n).get('name', pid)
    print(f'  {pname} controls:')
    for oname, etype, role in sorted(orgs, key=lambda x: x[0]):
        print(f'    {etype}: {role} -> {oname}')
    print()

# BELINGER LLC and MESAVILLE HOLDINGS LLC property APNs
print('=== PROPERTY APNs ===')
for tid in target_nodes:
    n = nm[tid]
    p = props(n)
    name = p.get('name', tid)
    props_list = []
    apns = set()
    for e in edges:
        if e.get('source_id') == tid and e['type'] == 'OWNS':
            t = nm.get(e.get('target_id'))
            if t and ntype(t) == 'PROPERTY':
                tp = props(t)
                apn = tp.get('apn', t['id'])
                apns.add(apn)
                props_list.append(tp)
    
    print(f'  {name}:')
    print(f'    Property count: {len(apns)}')
    if apns:
        sorted_apns = sorted(apns)
        print(f'    APN range: {sorted_apns[0]} to {sorted_apns[-1]}')
        print(f'    All APNs: {", ".join(sorted_apns)}')
    print()

# Cross-reference BELAVITA's 94 properties (from earlier finding)
print('=== BELAVITA LLC PROPERTY APN RANGE ===')
belavita_id = None
for tid in target_nodes:
    n = nm[tid]
    p = props(n)
    if p.get('name', '').upper() == 'BELAVITA LLC':
        belavita_id = tid
        break

if belavita_id:
    belavita_apns = []
    for e in edges:
        if e.get('source_id') == belavita_id and e['type'] == 'OWNS':
            t = nm.get(e.get('target_id'))
            if t and ntype(t) == 'PROPERTY':
                tp = props(t)
                belavita_apns.append(tp.get('apn', t['id']))
    belavita_apns = sorted(set(belavita_apns))
    print(f'  Total APNs: {len(belavita_apns)}')
    print(f'  Range: {belavita_apns[0]} to {belavita_apns[-1]}')
    print(f'  APNs: {", ".join(belavita_apns)}')
    print()

# Also check registered agent address links
print('=== REGISTERED AGENT / MAILING ADDRESS ===')
for tid in target_nodes:
    n = nm[tid]
    p = props(n)
    name = p.get('name', tid)
    for e in edges:
        if e.get('source_id') == tid and e['type'] == 'REGISTERED_AT':
            at = nm.get(e.get('target_id'))
            if at:
                ap = props(at)
                aid = ap.get('address') or ap.get('street') or at.get('id', '')
                print(f'  {name} REGISTERED_AT: {aid}, {ap.get("city","")}, {ap.get("state","")} {ap.get("zip","")}'.strip(', ') )
    for e in edges:
        if (e.get('source_id') == tid or e.get('target_id') == tid) and e['type'] == 'LOCATED_IN':
            other = e.get('target_id') if e.get('source_id') == tid else e.get('source_id')
            ot = nm.get(other)
            if ot and ntype(ot) == 'ADDRESS':
                op = props(ot)
                oid = op.get('address') or op.get('street') or ot.get('id', '')
                print(f'  {name} LOCATED_IN: {oid}, {op.get("city","")}, {op.get("state","")} '.strip(', '))
    print()

# Show all properties with addresses
print('=== PROPERTY ADDRESSES ===')
for tid in target_nodes:
    n = nm[tid]
    p = props(n)
    name = p.get('name', tid)
    for e in edges:
        if e.get('source_id') == tid and e['type'] == 'OWNS':
            prop = nm.get(e.get('target_id'))
            if prop and ntype(prop) == 'PROPERTY':
                pp = props(prop)
                apn = pp.get('apn', prop['id'])
                # Get address via LOCATED_IN
                addr = 'No address link'
                for e2 in edges:
                    if e2.get('source_id') == prop['id'] and e2['type'] == 'LOCATED_IN':
                        an = nm.get(e2.get('target_id'))
                        if an:
                            ap2 = props(an)
                            a2id = ap2.get('address') or ap2.get('street') or ''
                            addr = f"{a2id}, {ap2.get('city','')}, {ap2.get('state','')} {ap2.get('zip','')}".strip(', ')
                print(f'  {name} -> {apn} at {addr}')
    print()
