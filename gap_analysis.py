"""Graph gap analysis — what exists and what's missing."""
import json
from collections import Counter

with open("nodes.json") as f:
    nodes = json.load(f)
with open("edges.json") as f:
    edges = json.load(f)

# ── Nodes: label breakdown ──
label_counts = Counter()
for n in nodes:
    label = n.get("label", "UNKNOWN")
    label_counts[label] += 1

print("=== NODE LABEL BREAKDOWN ===")
for label, count in sorted(label_counts.items(), key=lambda x: -x[1]):
    print(f"  {label}: {count}")

print()

# ── Edges: type breakdown ──
type_counts = Counter()
for e in edges:
    t = e.get("type", "UNKNOWN")
    type_counts[t] += 1

print("=== EDGE TYPE BREAKDOWN ===")
for t, count in sorted(type_counts.items(), key=lambda x: -x[1]):
    print(f"  {t}: {count}")

print()

# ── Node IDs for quick lookup ──
node_ids = set()
node_by_id = {}
node_label_map = {}  # id -> label
for n in nodes:
    nid = n.get("id") or n.get("entity_id")
    node_ids.add(nid)
    node_by_id[nid] = n
    node_label_map[nid] = n.get("label", "UNKNOWN")

edge_ids_source = set()
edge_ids_target = set()
for e in edges:
    edge_ids_source.add(e.get("source") or e.get("source_id"))
    edge_ids_target.add(e.get("target") or e.get("target_id"))

# ── Orphan nodes (no edges at all) ──
connected_ids = edge_ids_source | edge_ids_target
orphans = node_ids - connected_ids
print(f"=== ORPHAN NODES (no edges) ===")
print(f"  Count: {len(orphans)}")
orphan_labels = Counter()
for oid in orphans:
    orphan_labels[node_label_map.get(oid, "UNKNOWN")] += 1
for label, count in sorted(orphan_labels.items(), key=lambda x: -x[1]):
    print(f"  {label}: {count}")

print()

# ── ORGANIZATION nodes with/without people ──
org_ids = set()
for n in nodes:
    if n.get("label") in ("ORGANIZATION", "ORG"):
        nid = n.get("id") or n.get("entity_id")
        org_ids.add(nid)

# Build adjacency
org_to_people = {}  # org_id -> set of person/attorney IDs
person_to_orgs = {}  # person_id -> set of org IDs
attorney_to_orgs = {}
for e in edges:
    src = e.get("source") or e.get("source_id")
    tgt = e.get("target") or e.get("target_id")
    etype = e.get("type")
    # Person/attorney -> ORG edges
    for s, t in [(src, tgt), (tgt, src)]:
        lbl = node_label_map.get(s, "")
        if lbl in ("PERSON", "ATTORNEY") and t in org_ids:
            if t not in org_to_people:
                org_to_people[t] = set()
            org_to_people[t].add(s)
        if lbl in ("PERSON", "ATTORNEY") and s in org_ids:
            if s not in org_to_people:
                org_to_people[s] = set()
            org_to_people[s].add(t)
    # OFFICER_OF edges specifically
    if etype == "OFFICER_OF" and src in org_ids and tgt in node_ids:
        if src not in org_to_people:
            org_to_people[src] = set()
        org_to_people[src].add(tgt)
    if etype == "OFFICER_OF" and tgt in org_ids and src in node_ids:
        if tgt not in org_to_people:
            org_to_people[tgt] = set()
        org_to_people[tgt].add(src)
    # REPRESENTS / REPRESENTED_BY
    for s, t in [(src, tgt), (tgt, src)]:
        if etype in ("REPRESENTS", "REPRESENTED_BY") and s in org_ids:
            if s not in org_to_people:
                org_to_people[s] = set()
            org_to_people[s].add(t)

orgs_with_people = set()
orgs_without_people = set()
for oid in org_ids:
    if oid in org_to_people and org_to_people[oid]:
        orgs_with_people.add(oid)
    else:
        orgs_without_people.add(oid)

def get_name(nid):
    n = node_by_id.get(nid, {})
    return n.get("name", n.get("text", nid[:20]))

print("=== ORGANIZATIONS: People Coverage ===")
print(f"  Total ORGs: {len(org_ids)}")
print(f"  With people/attorneys: {len(orgs_with_people)}")
print(f"  Without people/attorneys: {len(orgs_without_people)}")
print(f"  Coverage gap: {len(orgs_without_people)}/{len(org_ids)} ({100*len(orgs_without_people)//len(org_ids) if org_ids else 0}%)")

print()
print("=== TOP 20 ORGANIZATIONS BY PEOPLE CONNECTED ===")
orgby = sorted(org_to_people.items(), key=lambda x: -len(x[1]))
for oid, people in orgby[:20]:
    names = [get_name(p) for p in list(people)[:5]]
    print(f"  {get_name(oid)[:60]}: {len(people)} people [{', '.join(names)}{'...' if len(people) > 5 else ''}]")

print()
print("=== SAMPLE ORGS WITHOUT ANY PEOPLE ===")
count = 0
for oid in sorted(orgs_without_people, key=lambda x: get_name(x))[:20]:
    print(f"  {get_name(oid)[:70]}")
    count += 1
print(f"  (showing {count} of {len(orgs_without_people)})")

print()
# ── Edge types involving ORGs ──
print("=== EDGE TYPES INVOLVING ORGANIZATIONS ===")
org_edge_types = Counter()
for e in edges:
    src = e.get("source") or e.get("source_id")
    tgt = e.get("target") or e.get("target_id")
    etype = e.get("type")
    if src in org_ids or tgt in org_ids:
        org_edge_types[etype] += 1
for t, count in sorted(org_edge_types.items(), key=lambda x: -x[1]):
    print(f"  {t}: {count}")
