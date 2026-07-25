"""Trace actual registered address for BELAVITA LLC."""
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

# Find BELAVITA LLC org nodes
belavita = [n for n in nodes if n.get("label") in ("ORGANIZATION","ORG") and "BELAVITA" in (n.get("name","").upper())]
print(f"BELAVITA nodes: {len(belavita)}")
for b in belavita:
    bid = b.get("id") or b.get("entity_id")
    print(f"  id={bid}  name={b.get('name','?')}  props={json.dumps(b.get('properties',{}))[:200]}")

print("\n=== EDGES FROM FIRST BELAVITA ===")
if belavita:
    bid = belavita[0].get("id") or belavita[0].get("entity_id")
    for e in edges:
        src = e.get("source") or e.get("source_id")
        tgt = e.get("target") or e.get("target_id")
        if src == bid or tgt == bid:
            other_id = tgt if src == bid else src
            other = node_by_id.get(other_id, {})
            print(f"  {e.get('type','?')}: {other.get('label','?')} -> {other.get('name', other_id)[:60]}")

# Now find REGISTERED_AT edges to find address for any org
print("\n=== SAMPLE: ALL REGISTERED_AT TARGETS ===")
reg_targets = defaultdict(int)
for e in edges:
    if e.get("type") == "REGISTERED_AT":
        tgt = e.get("target") or e.get("target_id")
        reg_targets[tgt] += 1

# Show top 10 addresses
for tid, count in sorted(reg_targets.items(), key=lambda x: -x[1])[:10]:
    addr = node_by_id.get(tid, {})
    print(f"  {addr.get('name',tid)[:55]} ({addr.get('id','')[:40]}): {count} orgs")
