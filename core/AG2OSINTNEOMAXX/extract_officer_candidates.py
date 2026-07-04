"""Extract any existing person-to-organization links from the graph for top 20 targets."""
import json
from collections import defaultdict

with open("nodes.json") as f:
    nodes = json.load(f)
with open("edges.json") as f:
    edges = json.load(f)

# Build lookup
node_by_id = {}
for n in nodes:
    nid = n.get("id") or n.get("entity_id")
    node_by_id[nid] = n

# Top 20 landlord target names (from gap analysis)
target_names = [
    "BELAVITA LLC", "PENINSULA VILLAGE LLC", "OSF NB LLC",
    "JASMINE PLACE ASSOCIATES LLC", "HS HOMES LLC", "SUPERIOR BEACH HOMES LLC",
    "SLATER I LLC", "M WESTLAND LLC", "LIDO PENINSULA CO LLC",
    "FOUNTAIN VALLEY RENTALS LLC", "BURKE MONARCH LLC", "M GAPCO LLC",
    "BCORE RETAIL BROOKHURST ADAMS LLC", "PL JETTY LLC", "HUNTINGTON LLC",
    "FOURCHER 4340 LLC", "HUNTINGTON SANDS LLC", "PP TANGO CA LLC",
    "10477 HOLDINGS LLC", "KEN TRAN PROPERTIES LLC",
]

# Find target org IDs
target_ids = set()
target_id_to_name = {}
for n in nodes:
    if n.get("label") in ("ORGANIZATION", "ORG"):
        name = n.get("name", "").upper().strip()
        if any(t.upper() in name or name in t.upper() for t in target_names):
            nid = n.get("id") or n.get("entity_id")
            target_ids.add(nid)
            target_id_to_name[nid] = n.get("name", nid)
            if name in target_names:
                pass  # exact match

# Find all edges involving these targets
print(f"=== TARGET ORGS FOUND: {len(target_ids)} ===")
for nid, name in sorted(target_id_to_name.items(), key=lambda x: x[1]):
    print(f"  {name}")

print()

# For each target, find connected persons via any edge type
target_person_links = defaultdict(list)
for e in edges:
    src = e.get("source") or e.get("source_id")
    tgt = e.get("target") or e.get("target_id")
    etype = e.get("type", "")
    props = e.get("properties", {})

    for target_id in target_ids:
        direction = None
        other = None
        if src == target_id:
            other = tgt
            direction = "out"
        elif tgt == target_id:
            other = src
            direction = "in"

        if other:
            other_node = node_by_id.get(other, {})
            other_label = other_node.get("label", "")
            other_name = other_node.get("name", other)
            if other_label == "PERSON":
                target_person_links[target_id].append({
                    "person_name": other_name,
                    "person_id": other,
                    "edge_type": etype,
                    "direction": direction,
                    "role": props.get("role", "")
                })

print("=== EXISTING PERSON LINKS TO TARGETS ===")
total_links = 0
for tid in target_ids:
    links = target_person_links.get(tid, [])
    if links:
        total_links += len(links)
        print(f"\n  {target_id_to_name[tid]}:")
        for l in links:
            print(f"    {l['person_name']} --[{l['edge_type']}:{l['role']}]--> ({l['direction']})")
    else:
        print(f"\n  {target_id_to_name[tid]}: NO PERSON LINKS")

print(f"\n\nTotal person-to-target links found: {total_links}")
print(f"Targets with at least one person link: {len(target_person_links)}/{len(target_ids)}")

# Generate officer enrichment CSV from these links
print("\n\n=== ENRICHMENT CSV (can feed to enrich_batch.py) ===")
print("Name,Role,Company")
seen = set()
for tid in target_ids:
    for l in target_person_links.get(tid, []):
        person_name = l["person_name"]
        # Clean up name
        if "," in person_name:
            parts = [p.strip() for p in person_name.split(",")]
            person_name = f"{parts[1]} {parts[0]}" if len(parts) >= 2 else person_name
        role = l["role"] if l["role"] else l["edge_type"]
        company = target_id_to_name[tid]
        key = (person_name.upper(), company.upper())
        if key not in seen:
            seen.add(key)
            print(f"{person_name},{role},{company}")
