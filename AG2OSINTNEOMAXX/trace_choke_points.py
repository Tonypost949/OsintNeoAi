"""Trace the three choke-point addresses for all orgs and any human threads."""
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

# Target addresses
target_addrs = {
    "FOUNTAIN_VALLEY": "11770 WARNER AVE STE 215",
    "COSTA_MESA": "3187 RED HILL AVE STE 213",
    "NEWPORT_BEACH": "220 NEWPORT CENTER DR",
}

# Find address nodes matching these
addr_nodes = {}
for n in nodes:
    if n.get("label") == "ADDRESS":
        addr_name = n.get("name", "").upper().strip()
        for key, target in target_addrs.items():
            if target.upper() in addr_name or addr_name in target.upper():
                nid = n.get("id") or n.get("entity_id")
                addr_nodes[key] = {"id": nid, "name": n.get("name", "")}

print("=== ADDRESS NODES FOUND ===")
for key, info in addr_nodes.items():
    print(f"  {key}: {info['name']} (id={info['id']})")

if not addr_nodes:
    print("  NONE FOUND — searching partial matches...")
    for n in nodes:
        if n.get("label") == "ADDRESS":
            name = n.get("name", "").upper()
            for key, target in target_addrs.items():
                words = target.upper().split()[:3]
                if all(w in name for w in words):
                    nid = n.get("id") or n.get("entity_id")
                    addr_nodes[key] = {"id": nid, "name": n.get("name", "")}
                    print(f"  {key}: {n.get('name')} (id={nid})")

print()

# Find all orgs REGISTERED_AT these addresses
addr_to_orgs = defaultdict(list)
org_to_addr = {}
for e in edges:
    etype = e.get("type", "")
    if etype == "REGISTERED_AT":
        src = e.get("source") or e.get("source_id")
        tgt = e.get("target") or e.get("target_id")
        for key, info in addr_nodes.items():
            if tgt == info["id"]:
                org_name = node_by_id.get(src, {}).get("name", src)
                addr_to_orgs[key].append({"org_id": src, "name": org_name})
                org_to_addr[src] = key

print("=== ORGANIZATIONS AT EACH CHOKE POINT ===")
all_org_ids = set()
for key in ["FOUNTAIN_VALLEY", "COSTA_MESA", "NEWPORT_BEACH"]:
    orgs = addr_to_orgs.get(key, [])
    print(f"\n  {key} ({target_addrs[key]}): {len(orgs)} orgs")
    for o in orgs[:30]:
        print(f"    {o['name'][:65]}")
        all_org_ids.add(o["org_id"])
    if len(orgs) > 30:
        print(f"    ... and {len(orgs)-30} more")
    total = 0

print(f"\n  Total unique orgs across all 3 addresses: {len(all_org_ids)}")

# Find all person edges for these orgs
print("\n=== HUMAN CONNECTIONS TO THESE ORGS ===")
person_links = []
for e in edges:
    src = e.get("source") or e.get("source_id")
    tgt = e.get("target") or e.get("target_id")
    etype = e.get("type", "")
    props = e.get("properties", {})

    for oid in all_org_ids:
        other = None
        if src == oid:
            other = tgt
        elif tgt == oid:
            other = src
        if other:
            other_node = node_by_id.get(other, {})
            if other_node.get("label") == "PERSON":
                person_links.append({
                    "org_id": oid,
                    "org_name": node_by_id.get(oid, {}).get("name", oid),
                    "person_name": other_node.get("name", other),
                    "person_id": other,
                    "edge_type": etype,
                    "role": props.get("role", ""),
                })

if person_links:
    for pl in person_links:
        print(f"  {pl['person_name']} --[{pl['edge_type']}:{pl['role']}]--> {pl['org_name']}")
else:
    print("  NONE — Zero human connections to any org at these addresses")

# Generate enrichment CSV
print(f"\n=== ENRICHMENT TARGET: {len(all_org_ids)} ORGS NEED OFFICERS ===")
print("Name,Role,Company")
for oid in sorted(all_org_ids, key=lambda x: node_by_id.get(x, {}).get("name", x)):
    org_name = node_by_id.get(oid, {}).get("name", oid)
    print(f",REGISTERED_AGENT,{org_name}")
    print(f",MANAGING_MEMBER,{org_name}")
