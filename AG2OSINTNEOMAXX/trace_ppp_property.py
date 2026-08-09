import json
from collections import defaultdict

with open('nodes.json') as f:
    nodes = json.load(f)
with open('edges.json') as f:
    edges = json.load(f)

nm = {n['id']: n for n in nodes}

def ntype(n):
    return n.get('label', n.get('type'))

def props(n):
    return n.get('properties', {})

# Find orgs that have both RECEIVED_PPP edges and OWNS->PROPERTY edges
ppp_orgs = {}
owns_prop_orgs = set()

for e in edges:
    if e['type'] == 'RECEIVED_PPP':
        s = nm.get(e['source_id'])
        if s and ntype(s) == 'ORGANIZATION':
            ppp_orgs.setdefault(e['source_id'], []).append(e)
    elif e['type'] == 'OWNS':
        t = nm.get(e['target_id'])
        if t and ntype(t) == 'PROPERTY':
            owns_prop_orgs.add(e['source_id'])

target_orgs = [oid for oid in ppp_orgs if oid in owns_prop_orgs]
print(f'Target orgs with PPP + Property: {len(target_orgs)}')
print()

# For each, gather details
details = []
for oid in target_orgs:
    n = nm[oid]
    p = props(n)
    name = p.get('name', oid)
    risk = p.get('risk_score', 'N/A')
    flagged = p.get('flagged_reason', 'N/A')

    # PPP amounts
    ppp_amounts = []
    ppp_forgiven = []
    ppp_states = []
    ppp_loans = []
    for e in ppp_orgs[oid]:
        ln = nm.get(e['target_id'])
        lp = props(ln) if ln else {}
        amt = lp.get('amount', lp.get('loan_amount', 'N/A'))
        forg = lp.get('forgiven_amount', lp.get('forgiveness_amount', 'N/A'))
        loc = lp.get('location', 'N/A')
        ppp_amounts.append(amt)
        if str(forg) not in ('N/A', '', 'nan'):
            ppp_forgiven.append(forg)
        ppp_states.append(loc if loc != 'N/A' else 'N/A')
        if ln:
            ppp_loans.append(lp)
    
    # Property details
    properties = []
    for e in edges:
        if e['type'] == 'OWNS' and e['source_id'] == oid:
            t = nm.get(e['target_id'])
            if t and ntype(t) == 'PROPERTY':
                properties.append(props(t))
                # Get address linked to property
                for e2 in edges:
                    if e2['type'] == 'LOCATED_IN' and e2['source_id'] == t['id']:
                        addr = nm.get(e2['target_id'])
                        if addr:
                            properties[-1]['_address'] = props(addr).get('street', addr['id'])

    # Mailing/registered address (follow REGISTERED_AT edge)
    mailing_addresses = []
    for e in edges:
        if e['type'] == 'REGISTERED_AT' and e['source_id'] == oid:
            ma = nm.get(e['target_id'])
            if ma:
                mp = props(ma)
                mailing_addresses.append(f"{mp.get('street','')}, {mp.get('city','')}, {mp.get('state','')} {mp.get('zip','')}".strip(', '))
    
    # Other orgs sharing same mailing address
    shared_count = 0
    shared_orgs = []
    for ma in mailing_addresses:
        for e in edges:
            if e['type'] == 'REGISTERED_AT':
                eaddr = nm.get(e['target_id'])
                if eaddr:
                    emp = props(eaddr)
                    eaddr_str = f"{emp.get('street','')}, {emp.get('city','')}, {emp.get('state','')}".strip(', ')
                    if eaddr_str == ma and e['source_id'] != oid:
                        shared_count += 1
                        shared_orgs.append(e['source_id'])
    
    total_ppp = sum(float(a) for a in ppp_amounts if str(a).replace('.','',1).replace('-','',1).isdigit())
    total_forgiven = sum(float(f) for f in ppp_forgiven if str(f).replace('.','',1).replace('-','',1).isdigit())
    
    details.append({
        'name': name,
        'oid': oid,
        'risk': risk,
        'flagged': flagged,
        'ppp_count': len(ppp_amounts),
        'total_ppp': total_ppp,
        'total_forgiven': total_forgiven,
        'ppp_states': list(set(ppp_states)),
        'properties': properties,
        'mailing_addresses': mailing_addresses,
        'shared_address_orgs': shared_count,
        'shared_org_names': [nm.get(o, {}).get('properties', {}).get('name', o) for o in shared_orgs[:5]]
    })

# Sort by total PPP descending
details.sort(key=lambda x: x['total_ppp'], reverse=True)

# Full report
print('='*80)
print(f'PPP + PROPERTY DEEP TRACE — {len(details)} Organizations')
print('='*80)
print()
for d in details:
    print(f'--- {d["name"]} ---')
    print(f'  Org ID: {d["oid"]}')
    print(f'  Risk: {d["risk"]} | Flagged: {d["flagged"]}')
    print(f'  PPP Loans: {d["ppp_count"]} | Total PPP: ${d["total_ppp"]:,.2f} | Forgiven: ${d["total_forgiven"]:,.2f}')
    print(f'  PPP States: {", ".join(d["ppp_states"])}')
    
    if d['properties']:
        for i, pr in enumerate(d['properties']):
            pr_type = pr.get('type', 'N/A')
            pr_val = pr.get('value', 'N/A')
            pr_addr = pr.get('_address', 'N/A')
            print(f'  Property {i+1}: type={pr_type}, value={pr_val}, address={pr_addr}')
    
    if d['mailing_addresses']:
        for ma in d['mailing_addresses']:
            print(f'  Mailing: {ma}')
    
    if d['shared_address_orgs'] > 0:
        print(f'  *** SHARED ADDRESS: {d["shared_address_orgs"]} other org(s) at same address')
        print(f'  *** Shared with: {", ".join(d["shared_org_names"][:3])}')
    
    # Score
    score = 'LOW'
    flags = []
    if d['total_ppp'] > 100000:
        flags.append('PPP > $100K')
    if d['shared_address_orgs'] >= 5:
        flags.append(f'Shared addr with {d["shared_address_orgs"]}+ orgs')
    if len(d['properties']) > 1:
        flags.append(f'{len(d["properties"])} properties')
    if d['ppp_count'] > 1:
        flags.append(f'{d["ppp_count"]} PPP loans')
    if d['flagged'] and str(d['flagged']) not in ('', 'nan', 'None'):
        flags.append(f'FLAGGED: {d["flagged"]}')
    
    if len(flags) >= 2:
        score = 'HIGH'
    elif len(flags) >= 1:
        score = 'MEDIUM'
    print(f'  SCORE: {score} | Flags: {", ".join(flags) if flags else "None"}')
    print()

# Aggregate
print('='*80)
print('AGGREGATE STATISTICS')
print('='*80)
total_ppp_all = sum(d['total_ppp'] for d in details)
total_forgiven_all = sum(d['total_forgiven'] for d in details)
print(f'Total PPP dollars across all {len(details)} orgs: ${total_ppp_all:,.2f}')
print(f'Total forgiven: ${total_forgiven_all:,.2f}')
print()

print('--- Top 10 Highest PPP Recipients ---')
for d in details[:10]:
    print(f'  ${d["total_ppp"]:>10,.2f} | {d["name"]}')
print()

print('--- Top 10 Mailing Addresses as Hub Locations ---')
addr_count = defaultdict(int)
addr_orgs = defaultdict(list)
for d in details:
    for ma in d['mailing_addresses']:
        addr_count[ma] += 1
        addr_orgs[ma].append(d['name'])
for ma, cnt in sorted(addr_count.items(), key=lambda x: -x[1])[:10]:
    print(f'  {cnt:>3} orgs | {ma}')
    for o in addr_orgs[ma][:3]:
        print(f'           - {o}')
print()

print('--- Score Summary ---')
high = sum(1 for d in details if 'HIGH' in str(d))
# Actually recalculate
high_count = sum(1 for d in details if sum(1 for f in (['PPP > $100K'] if d['total_ppp'] > 100000 else []) + (['Shared'] if d['shared_address_orgs'] >= 5 else []) + ([f'{len(d["properties"])} properties'] if len(d["properties"]) > 1 else []) + ([f'{d["ppp_count"]} PPP loans'] if d['ppp_count'] > 1 else [])) >= 2)

# Restat
high_orgs = []
med_orgs = []
low_orgs = []
for d in details:
    sigs = 0
    if d['total_ppp'] > 100000: sigs += 1
    if d['shared_address_orgs'] >= 5: sigs += 1
    if len(d['properties']) > 1: sigs += 1
    if d['ppp_count'] > 1: sigs += 1
    if d['flagged'] and str(d['flagged']) not in ('', 'nan', 'None'): sigs += 1
    if sigs >= 2:
        high_orgs.append(d['name'])
    elif sigs >= 1:
        med_orgs.append(d['name'])
    else:
        low_orgs.append(d['name'])

print(f'HIGH: {len(high_orgs)} orgs')
for o in high_orgs:
    print(f'  - {o}')
print(f'MEDIUM: {len(med_orgs)} orgs')
for o in med_orgs[:20]:
    print(f'  - {o}')
if len(med_orgs) > 20:
    print(f'  ... and {len(med_orgs) - 20} more')
print(f'LOW: {len(low_orgs)} orgs')
for o in low_orgs[:20]:
    print(f'  - {o}')
if len(low_orgs) > 20:
    print(f'  ... and {len(low_orgs) - 20} more')
