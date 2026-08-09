"""Generate prioritized target list for enrichment."""
import json
from collections import Counter

with open("nodes.json") as f:
    nodes = json.load(f)
with open("edges.json") as f:
    edges = json.load(f)

node_by_id = {}
org_ids = set()
property_ids = set()
person_ids = set()
for n in nodes:
    nid = n.get("id") or n.get("entity_id")
    node_by_id[nid] = n
    lbl = n.get("label", "")
    if lbl in ("ORGANIZATION", "ORG"):
        org_ids.add(nid)
    elif lbl == "PROPERTY":
        property_ids.add(nid)
    elif lbl == "PERSON":
        person_ids.add(nid)

# Properties owned per org
org_prop_count = Counter()
org_ppp = set()
person_connections = Counter()  # org -> count of connected PERSON nodes

for e in edges:
    src = e.get("source") or e.get("source_id")
    tgt = e.get("target") or e.get("target_id")
    etype = e.get("type", "")
    if etype == "OWNS" and src in org_ids and tgt in property_ids:
        org_prop_count[src] += 1
    if etype == "RECEIVED_PPP" and src in org_ids:
        org_ppp.add(src)
    # Track existing person connections
    for s, t in [(src, tgt), (tgt, src)]:
        if s in org_ids and t in person_ids:
            person_connections[s] += 1

# Shared address hubs
addr_orgs = {}
for e in edges:
    src = e.get("source") or e.get("source_id")
    tgt = e.get("target") or e.get("target_id")
    etype = e.get("type", "")
    if etype == "REGISTERED_AT" and src in org_ids:
        addr = node_by_id.get(tgt, {}).get("name", "")
        if addr not in addr_orgs:
            addr_orgs[addr] = []
        addr_orgs[addr].append(src)

def name_of(nid):
    return node_by_id.get(nid, {}).get("name", nid[:40])

print("=" * 100)
print("PRIORITY TARGET LIST FOR ENRICHMENT")
print("=" * 100)

# ── List A: Top Landlords (by properties) ──
print("\n--- LIST A: TOP 50 LANDLORDS (highest property count) ---")
print(f"{'#':>3} {'Org Name':<55} {'Props':>6} {'PPP':>4} {'People':>6} {'HubAddr':>7}")
print("-" * 85)
for i, (oid, count) in enumerate(org_prop_count.most_common(50), 1):
    name = name_of(oid)
    ppp = "Y" if oid in org_ppp else ""
    ppl = person_connections.get(oid, 0)
    hub = sum(1 for a, orgs in addr_orgs.items() if oid in orgs and len(orgs) > 1)
    print(f"{i:>3} {name[:54]:<55} {count:>6} {ppp:>4} {ppl:>6} {hub:>7}")

# ── List B: Address Hubs ──
print("\n\n--- LIST B: TOP 20 ADDRESS HUBS (most orgs at same address) ---")
for addr, orgs in sorted(addr_orgs.items(), key=lambda x: -len(x[1]))[:20]:
    has_ppp = sum(1 for o in orgs if o in org_ppp)
    has_people = sum(1 for o in orgs if person_connections.get(o, 0) > 0)
    print(f"\n  {addr[:70]}")
    print(f"    Orgs: {len(orgs)} | With PPP: {has_ppp} | With people: {has_people}")
    top_orgs = sorted(orgs, key=lambda o: -org_prop_count.get(o, 0))[:5]
    for o in top_orgs:
        print(f"      - {name_of(o)[:55]} ({org_prop_count.get(o, 0)} props)")

# ── List C: PPP Borrowers without people ──
print("\n\n--- LIST C: PPP BORROWERS WITHOUT ANY PEOPLE ---")
ppp_no_people = [o for o in org_ppp if person_connections.get(o, 0) == 0]
for oid in sorted(ppp_no_people, key=lambda x: -org_prop_count.get(x, 0))[:30]:
    print(f"  {name_of(oid)[:65]} ({org_prop_count.get(oid, 0)} props)")

# ── Summary ──
print("\n\n=== SUMMARY ===")
print(f"Total organizations:                 {len(org_ids)}")
print(f"  Own property:                     {len(org_prop_count)}")
print(f"  Have PPP:                         {len(org_ppp)}")
print(f"  Have people connected:            {len(person_connections)}")
print(f"  Address hubs (>=10 orgs):         {sum(1 for a,o in addr_orgs.items() if len(o) >= 10)}")
print(f"  Address hubs (>=50 orgs):         {sum(1 for a,o in addr_orgs.items() if len(o) >= 50)}")
print(f"Total PERSON nodes in graph:        {len(person_ids)}")
print(f"  Connected to any org:             {sum(1 for o in person_connections.values() if o > 0)}")
print()
print("TOP 10 ORGS FOR IMMEDIATE ENRICHMENT:")
# Combine signals: property count + PPP + hub density
scored = []
for oid in org_ids:
    score = org_prop_count.get(oid, 0) * 3
    if oid in org_ppp:
        score += 10
    hub_score = sum(1 for a, orgs in addr_orgs.items() if oid in orgs and len(orgs) > 1)
    score += hub_score * 2
    # Penalize if already has people
    if person_connections.get(oid, 0) > 0:
        score -= 5
    scored.append((score, oid))
scored.sort(reverse=True)
for score, oid in scored[:10]:
    name = name_of(oid)
    props = org_prop_count.get(oid, 0)
    ppp = "Y" if oid in org_ppp else ""
    ppl = person_connections.get(oid, 0)
    print(f"  Score {score:>3}: {name[:55]} ({props} props, PPP={ppp}, people={ppl})")
