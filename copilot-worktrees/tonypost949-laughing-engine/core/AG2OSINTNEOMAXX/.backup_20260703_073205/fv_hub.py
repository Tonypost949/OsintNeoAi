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

# Find FOUNTAIN VALLEY address nodes
fv_addrs = []
for n in nodes:
    p = props(n)
    city = str(p.get('city', '')).strip().upper()
    addr = str(p.get('address', p.get('street', ''))).strip().upper()
    if 'FOUNTAIN VALLEY' in city or 'FOUNTAIN VALLEY' in addr:
        fv_addrs.append(n['id'])

print(f'=== FOUNTAIN VALLEY HUB EXPANSION ===')
print(f'Address nodes found: {len(fv_addrs)}')
print()

# Map address -> orgs via REGISTERED_AT edges
addr_orgs = defaultdict(list)
for e in edges:
    if e['type'] == 'REGISTERED_AT':
        tid = e.get('target_id', e.get('target'))
        if tid in fv_addrs:
            addr_orgs[tid].append(e['source_id'])

# Also find orgs whose OWNED property address is in FV
for e in edges:
    if e['type'] == 'OWNS':
        t = nm.get(e['target_id'])
        if t and ntype(t) == 'PROPERTY':
            tp = props(t)
            prop_addr = str(tp.get('address', '')).upper()
            if 'FOUNTAIN VALLEY' in prop_addr:
                # Find the LOCATED_IN edge for this property to get the structured address
                for e2 in edges:
                    if e2['type'] == 'LOCATED_IN' and e2['source_id'] == t['id']:
                        aid = e2['target_id']
                        if aid in fv_addrs:
                            addr_orgs[aid].append(e['source_id'])

# 1. Exact shared address(es)
print('--- 1. EXACT ADDRESSES ---')
for aid in sorted(addr_orgs.keys(), key=lambda x: -len(addr_orgs[x])):
    n = nm[aid]
    p = props(n)
    addr_str = f"{p.get('address','')}, {p.get('city','')}, {p.get('state','')} {p.get('zip','')}".strip(', ')
    orgs = list(set(addr_orgs[aid]))
    print(f'  {addr_str}  [{p.get("type","ADDRESS")}]')
    print(f'    -> {len(orgs)} unique organizations')
print()

# 2-5: Gather all orgs in FV hub
all_org_ids = set()
for orgs in addr_orgs.values():
    all_org_ids.update(orgs)

# Collect all unique org-to-address mappings
org_address_map = defaultdict(set)
for aid, orgs in addr_orgs.items():
    n = nm[aid]
    p = props(n)
    addr_str = f"{p.get('address','')}, {p.get('city','')}, {p.get('state','')}".strip(', ')
    for oid in orgs:
        org_address_map[oid].add(addr_str)

# For each org, get PPP loan info
org_ppp = defaultdict(list)
org_props = defaultdict(list)
for e in edges:
    if e['type'] == 'RECEIVED_PPP':
        t = nm.get(e['target_id'])
        if t:
            tp = props(t)
            amt = tp.get('amount', '0')
            forg = tp.get('forgiven_amount', '0')
            org_ppp[e['source_id']].append((amt, forg, tp.get('status', '')))
    if e['type'] == 'OWNS':
        t = nm.get(e['target_id'])
        if t and ntype(t) == 'PROPERTY':
            org_props[e['source_id']].append(t['id'])

print(f'--- 2. ALL ORGANIZATIONS ---')
print(f'Total unique orgs in FOUNTAIN VALLEY hub: {len(all_org_ids)}')
print()
# Sort by PPP amount descending
sorted_orgs = sorted(all_org_ids, key=lambda o: sum(float(a) for a, f, s in org_ppp.get(o, [[0,'0','']]) if str(a).replace('.','',1).replace('-','',1).isdigit()), reverse=True)

for oid in sorted_orgs[:50]:
    n = nm.get(oid)
    if not n:
        continue
    name = props(n).get('name', oid)
    addrs = org_address_map.get(oid, set())
    ppp = org_ppp.get(oid, [])
    total_ppp = sum(float(a) for a, f, s in ppp if str(a).replace('.','',1).replace('-','',1).isdigit())
    total_forgiven = sum(float(f) for a, f, s in ppp if str(f).replace('.','',1).replace('-','',1).isdigit())
    prop_count = len(org_props.get(oid, []))
    ppp_count = len(ppp)
    
    print(f'  {name}')
    for a in addrs:
        print(f'    Address: {a}')
    if ppp_count > 0:
        print(f'    PPP loans: {ppp_count} | Total: ${total_ppp:,.2f} | Forgiven: ${total_forgiven:,.2f}')
        for amt, forg, status in ppp:
            print(f'      Amount: ${float(amt):,.2f} | Forgiven: ${float(forg):,.2f} | Status: {status}')
    if prop_count > 0:
        print(f'    Properties: {prop_count}')
    print()

print('--- 4. ORGANIZATIONS WITH MULTIPLE PROPERTIES ---')
multi_props = [(oid, org_props[oid]) for oid in all_org_ids if len(org_props.get(oid, [])) > 1]
for oid, props_list in sorted(multi_props, key=lambda x: -len(x[1])):
    n = nm.get(oid)
    name = props(n).get('name', oid) if n else oid
    print(f'  {name} -> {len(props_list)} properties: {props_list}')
print()

print('--- 5. ORGANIZATIONS WITH MULTIPLE PPP LOANS ---')
multi_ppp = [(oid, org_ppp[oid]) for oid in all_org_ids if len(org_ppp.get(oid, [])) > 1]
for oid, ppp_list in sorted(multi_ppp, key=lambda x: -len(x[1])):
    n = nm.get(oid)
    name = props(n).get('name', oid) if n else oid
    total = sum(float(a) for a, f, s in ppp_list if str(a).replace('.','',1).replace('-','',1).isdigit())
    print(f'  {name} -> {len(ppp_list)} PPP loans, total ${total:,.2f}')
print()

# 6. Top 50 entities by connectivity - find all nodes connected to FV orgs via any edge
print('--- 6. TOP 50 ENTITIES BY CONNECTIVITY ---')
fv_org_set = set(all_org_ids)
connected_degree = defaultdict(int)
for e in edges:
    src = e.get('source_id', e.get('source'))
    tgt = e.get('target_id', e.get('target'))
    if src in fv_org_set:
        connected_degree[tgt] += 1
    if tgt in fv_org_set:
        connected_degree[src] += 1
# Filter to only entities connected to FV hub
for rank, (eid, deg) in enumerate(sorted(connected_degree.items(), key=lambda x: -x[1])[:50], 1):
    n = nm.get(eid)
    if n:
        nt = ntype(n)
        p = props(n)
        ename = p.get('name', p.get('address', p.get('street', eid)))
        if len(str(ename)) > 60:
            ename = str(ename)[:57] + '...'
        print(f'  {rank:>3}. [{nt:15s}] {ename:<60s} (deg: {deg})')
    else:
        print(f'  {rank:>3}. [UNKNOWN          ] {str(eid):<60s} (deg: {deg})')
