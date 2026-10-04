"""Find address nodes matching the three choke points."""
import json
from collections import defaultdict

with open("nodes.json") as f:
    nodes = json.load(f)

addrs = [n for n in nodes if n.get("label") == "ADDRESS"]
print(f"Total ADDRESS nodes: {len(addrs)}")

# Search for matches
keywords = {"FOUNTAIN_VALLEY": ["WARNER"], "COSTA_MESA": ["RED HILL"], "NEWPORT_BEACH": ["NEWPORT CENTER"]}
for key, kws in keywords.items():
    matches = []
    for a in addrs:
        name = (a.get("name") or "").upper()
        props = (str(a.get("properties", {})) or "").upper()
        combined = name + "|" + props
        if all(k in combined for k in kws):
            matches.append(a)
    print(f"\n{key}: {len(matches)} address nodes")
    for m in matches[:5]:
        print(f"  id={m.get('id','?')}  name={m.get('name','?')}")

# Look at the raw structure of a few address nodes
print("\n\nSample ADDRESS node structures:")
count = 0
for a in addrs[:5]:
    print(f"\n  {json.dumps(a, indent=2)[:300]}")
    count += 1
