import json
from collections import Counter, defaultdict

with open('nodes.json') as f:
    nodes = json.load(f)
with open('edges.json') as f:
    edges = json.load(f)

nm = {n['id']: n for n in nodes}

def nd(e, side):
    return nm.get(e.get(f'{side}_id') or e.get(side))

def ntype(n):
    return n.get('label', n.get('type'))

# 1. ORGs with PPP + Property
ppp_orgs = set()
prop_orgs = set()
for e in edges:
    s = nd(e, 'source')
    t = nd(e, 'target')
    if e['type'] == 'RECEIVED_PPP' and s and ntype(s) == 'ORGANIZATION':
        ppp_orgs.add(e['source_id'])
    if e['type'] == 'OWNS' and t and ntype(t) == 'PROPERTY':
        prop_orgs.add(e['source_id'])

overlap = ppp_orgs & prop_orgs
print('=== ORGs with PPP + Property ===')
for oid in sorted(overlap)[:15]:
    n = nm[oid]
    p = n.get('properties', {})
    print(f'  {p.get("name", oid)} | risk: {p.get("risk_score","N/A")} | flag: {p.get("flagged_reason","N/A")}')
print(f'  Total: {len(overlap)}\n')

# 2. Persons connected to 2+ ORGs
po = defaultdict(set)
for e in edges:
    if e['type'] in ('OFFICER_OF', 'OWNS', 'DIRECTOR_OF'):
        s = nd(e, 'source')
        t = nd(e, 'target')
        if s and t and ntype(s) == 'PERSON' and ntype(t) == 'ORGANIZATION':
            po[e['source_id']].add(e['target_id'])

multi = {k: v for k, v in po.items() if len(v) >= 2}
print('=== Persons in 2+ ORGs ===')
for pid, orgs in sorted(multi.items(), key=lambda x: -len(x[1]))[:15]:
    name = nm[pid].get('properties', {}).get('name', pid)
    onames = [nm[o].get('properties', {}).get('name', o[:25]) for o in list(orgs)[:5]]
    print(f'  {name} -> {len(orgs)} orgs: {onames}')
print(f'  Total: {len(multi)}\n')

# 3. High-risk ORGs with PPP
print('=== High-Risk Flagged ORGs with PPP ===')
hr = []
for oid in ppp_orgs:
    n = nm.get(oid)
    if n:
        p = n.get('properties', {})
        r = str(p.get('risk_score', ''))
        f = str(p.get('flagged_reason', ''))
        if r not in ('', 'nan', 'None', '0') or f not in ('', 'nan', 'None'):
            hr.append((p.get('name', oid), r, f))
for name, r, f in sorted(hr, key=lambda x: x[1], reverse=True)[:15]:
    print(f'  {name} | risk: {r} | flagged: {f}')
print(f'  Total: {len(hr)}\n')

# 4. Same-address shell clusters
ao = defaultdict(list)
for e in edges:
    if e['type'] == 'REGISTERED_AT':
        t = nd(e, 'target')
        s = nd(e, 'source')
        if t and s and ntype(t) == 'ADDRESS' and ntype(s) == 'ORGANIZATION':
            street = t.get('properties', {}).get('street', t['id'])
            ao[street].append(e['source_id'])

cl = {a: orgs for a, orgs in ao.items() if len(orgs) >= 3}
print('=== 3+ ORGs at Same Address ===')
for addr, orgs in sorted(cl.items(), key=lambda x: -len(x[1]))[:15]:
    names = [nm[o].get('properties', {}).get('name', o[:25]) for o in orgs]
    print(f'  {str(addr)[:60]} -> {len(orgs)} orgs: {names[:6]}')
print(f'  Total clusters: {len(cl)}\n')

# 5. Top connected persons
print('=== Top Connected Persons ===')
pd = defaultdict(int)
for e in edges:
    s = nd(e, 'source')
    t = nd(e, 'target')
    if s and ntype(s) == 'PERSON':
        pd[e['source_id']] += 1
    if t and ntype(t) == 'PERSON':
        pd[e['target_id']] += 1
for pid, deg in sorted(pd.items(), key=lambda x: -x[1])[:10]:
    n = nm[pid]
    name = n.get('properties', {}).get('name', pid[:40])
    print(f'  {name} -> {deg} connections')

# 6. Agents serving multiple ORGs
print('\n=== Registered Agents serving multiple ORGs ===')
ago = defaultdict(list)
for e in edges:
    if e['type'] == 'OFFICER_OF':
        s = nd(e, 'source')
        t = nd(e, 'target')
        if s and t and ntype(s) == 'PERSON' and ntype(t) == 'ORGANIZATION':
            ago[e['source_id']].append(e['target_id'])
ma = {a: orgs for a, orgs in ago.items() if len(orgs) >= 2}
for aid, orgs in sorted(ma.items(), key=lambda x: -len(x[1]))[:10]:
    aname = nm[aid].get('properties', {}).get('name', aid[:30])
    onames = [nm[o].get('properties', {}).get('name', o[:25]) for o in orgs[:5]]
    print(f'  {aname} -> {len(orgs)} ORGs: {onames}')
print(f'  Total multi-ORG agents: {len(ma)}\n')

# 7. Litigation stats
print('=== Litigation ===')
lit_persons = set()
for e in edges:
    if e['type'] == 'LITIGANT_IN':
        s = nd(e, 'source')
        if s and ntype(s) == 'PERSON':
            lit_persons.add(e['source_id'])
print(f'  Persons in litigation: {len(lit_persons)}')

# 8. Attorneys linked to multiple orgs
print('\n=== Attorneys per ORG count ===')
atyo = defaultdict(list)
for e in edges:
    if e['type'] == 'REPRESENTED_BY':
        t = nd(e, 'target')
        s = nd(e, 'source')
        if t and s and ntype(t) == 'ATTORNEY':
            atyo[e['target_id']].append(e['source_id'])
for aid, orgs in sorted(atyo.items(), key=lambda x: -len(x[1]))[:10]:
    aname = nm[aid].get('properties', {}).get('name', aid[:30])
    print(f'  {aname} -> {len(orgs)} ORGs')
print(f'  Total attorneys: {len(atyo)}')
