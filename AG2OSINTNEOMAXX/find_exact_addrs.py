"""Find exact choke-point addresses and all orgs registered at them."""
import json
from collections import defaultdict

with open("nodes.json") as f:
    nodes = json.load(f)
with open("edges.json") as f:
    edges = json.load(f)

node_by_id = {}
for n in nodes:
    nid = n.get("id") or n.get("entity_id")
    node_by_id[nid] = n

# Search for exact address matches
searches = [
    ("11770 WARNER", "11770 WARNER AVE STE 215"),
    ("3187 RED HILL", "3187 RED HILL AVE STE 213"),
    ("220 NEWPORT CENTER", "220 NEWPORT CENTER DR"),
]

addr_ids = {}
for label, target in searches:
    matches = []
    for n in nodes:
        if n.get("label") == "ADDRESS":
            nid = n.get("id", "").upper()
            name = (n.get("name") or "").upper()
            props = (str(n.get("properties", {})) or "").upper()
            combined = nid + "|" + name + "|" + props
            if target.upper() in combined or all(w.upper() in combined for w in target.split()[:2]):
                matches.append(n)
    print(f"\n{label} ({target}): {len(matches)} address nodes")
    for m in matches:
        print(f"  id={m.get('id','?')}")
        addr_ids[label] = m.get("id")

# Find REGISTERED_AT edges for these address IDs
addr_to_orgs = defaultdict(list)
for e in edges:
    src = e.get("source") or e.get("source_id")
    tgt = e.get("target") or e.get("target_id")
    etype = e.get("type", "")
    if etype == "REGISTERED_AT":
        for label, aid in addr_ids.items():
            if tgt == aid:
                org = node_by_id.get(src, {})
                addr_to_orgs[label].append({
                    "org_id": src,
                    "name": org.get("name", src),
                    "props": org.get("properties", {}),
                })

print("\n\n=== ORGS AT EXACT CHOKE POINTS ===")
for label in ["11770 WARNER", "3187 RED HILL", "220 NEWPORT CENTER"]:
    orgs = addr_to_orgs.get(label, [])
    print(f"\n{label}: {len(orgs)} orgs")
    for o in orgs[:20]:
        print(f"  {o['name'][:65]}")
    if len(orgs) > 20:
        print(f"  ... and {len(orgs)-20} more")
