"""Check what person data we have in the graph."""
import json
from collections import Counter

with open("nodes.json") as f:
    nodes = json.load(f)

with open("edges.json") as f:
    edges = json.load(f)

people = [n for n in nodes if n.get("label") == "PERSON"]
print(f"Total PERSON nodes: {len(people)}")
print(f"Sample keys: {list(people[0].keys()) if people else 'none'}")

# Show person names and any affiliation data
print("\n=== SAMPLE PERSON NODES ===")
has_extra = 0
for p in people[:50]:
    nid = p.get("id") or p.get("entity_id") or "?"
    name = p.get("name", p.get("text", "unnamed"))
    extra = {k: v for k, v in p.items() if k not in ("id", "entity_id", "name", "text", "label", "type")}
    if extra:
        has_extra += 1
    desc = str(extra.get("description", extra.get("affiliations", "")))[:80]
    print(f"  {str(nid)[:20]:>20}  {str(name)[:45]:<45}  {desc}")

print(f"\nPeople with extra fields: {has_extra}/{len(people)}")

# Check if any person descriptions mention top 20 orgs
targets = ["BELAVITA", "PENINSULA VILLAGE", "OSF NB", "JASMINE PLACE",
           "HS HOMES", "SUPERIOR BEACH", "SLATER I", "M WESTLAND",
           "LIDO PENINSULA", "FOUNTAIN VALLEY RENTALS"]
matches = 0
for p in people:
    desc = str(p.get("description", "")).upper()
    name = str(p.get("name", "")).upper()
    combined = desc + "|" + name
    for t in targets:
        if t.upper() in combined:
            matches += 1
            break

print(f"\nPeople mentioning top 10 org names: {matches}")

# Check edges from/to PERSON nodes
person_ids = set()
for p in people:
    pid = p.get("id") or p.get("entity_id")
    person_ids.add(pid)

person_edges = Counter()
for e in edges:
    src = e.get("source") or e.get("source_id")
    tgt = e.get("target") or e.get("target_id")
    if src in person_ids:
        person_edges[e.get("type", "")] += 1
    if tgt in person_ids:
        person_edges[e.get("type", "")] += 1

print(f"\nEdge types involving PERSON nodes:")
for t, c in sorted(person_edges.items(), key=lambda x: -x[1]):
    print(f"  {t}: {c}")
