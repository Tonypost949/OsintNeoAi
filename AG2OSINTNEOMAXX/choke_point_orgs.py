"""Extract full org list for each choke point address and generate enrichment CSVs."""
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

target_ids = [
    "11770 WARNER AVE STE 215, FOUNTAIN VALLEY",
    "220 NEWPORT CENTER DR # 11-557, NEWPORT BEACH",
    "3187 RED HILL AVE STE 213, COSTA MESA",
]

# Build address -> orgs mapping
addr_orgs = {}
for tid in target_ids:
    addr_orgs[tid] = []

for e in edges:
    if e.get("type") == "REGISTERED_AT":
        src = e.get("source") or e.get("source_id")
        tgt = e.get("target") or e.get("target_id")
        addr_node = node_by_id.get(tgt, {})
        addr_name = addr_node.get("name") or addr_node.get("id", "")
        for tid in target_ids:
            if addr_name == tid:
                org = node_by_id.get(src, {})
                addr_orgs[tid].append({
                    "org_id": src,
                    "name": org.get("name", src),
                })

# Output for each address
all_org_names = set()
for addr in target_ids:
    orgs = addr_orgs[addr]
    label = addr.split(",")[0]
    print(f"\n{'='*60}")
    print(f"ADDRESS: {addr}")
    print(f"ORG COUNT: {len(orgs)}")
    print(f"{'='*60}")
    
    # Deduplicate by name
    seen = {}
    for o in orgs:
        name = o["name"]
        if name not in seen:
            seen[name] = 0
        seen[name] += 1
    
    # Sort by count (duplicates = multiple properties)
    for name in sorted(seen, key=lambda n: -seen[n]):
        count = seen[name]
        dup = f" ({count} properties)" if count > 1 else ""
        print(f"  {name[:65]}{dup}")
        all_org_names.add(name)

print(f"\n\n{'='*60}")
print(f"TOTAL UNIQUE ORGS ACROSS ALL 3 ADDRESSES: {len(all_org_names)}")
print(f"{'='*60}")

# Generate ready-to-use enrichment CSVs for each address
print(f"\n\n=== ENRICHMENT CSV (all 3 addresses) ===")
print("Name,Role,Company,Address")
addr_short = {"11770 WARNER AVE STE 215, FOUNTAIN VALLEY": "FOUNTAIN_VALLEY",
              "220 NEWPORT CENTER DR # 11-557, NEWPORT BEACH": "NEWPORT_BEACH",
              "3187 RED HILL AVE STE 213, COSTA MESA": "COSTA_MESA"}
for addr in target_ids:
    seen = set()
    for o in addr_orgs[addr]:
        name = o["name"]
        if name not in seen:
            seen.add(name)
            print(f",REGISTERED_AGENT,{name},{addr_short[addr]}")
            print(f",MANAGING_MEMBER,{name},{addr_short[addr]}")
