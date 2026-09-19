"""Examine PERSON node properties for affiliation data."""
import json

with open("nodes.json") as f:
    nodes = json.load(f)

people = [n for n in nodes if n.get("label") == "PERSON"]

# Show properties keys across people
prop_keys = set()
for p in people:
    props = p.get("properties", {})
    if isinstance(props, dict):
        prop_keys.update(props.keys())
    elif isinstance(props, str):
        prop_keys.add("_string_properties")

print(f"Property keys found: {sorted(prop_keys)}")

# Show first 10 people with their full properties
count = 0
for p in people:
    props = p.get("properties", {})
    if props:
        name = p.get("name", p.get("text", "unnamed"))
        if isinstance(props, dict) and props:
            print(f"\n  {name}")
            for k, v in props.items():
                print(f"    {k}: {str(v)[:100]}")
            count += 1
            if count >= 10:
                break
        elif isinstance(props, str) and props.strip():
            print(f"\n  {name}")
            print(f"    string_props: {props[:200]}")
            count += 1
            if count >= 10:
                break

# Check if any properties contain org names/roles
role_keywords = ["officer", "manager", "agent", "director", "president", "ceo", "member", "owner"]
org_keywords = ["llc", "inc", "corp", "company", "holdings"]
roles_found = 0
orgs_in_props = 0
for p in people:
    props = p.get("properties", {})
    if isinstance(props, str):
        low = props.lower()
        if any(kw in low for kw in role_keywords):
            roles_found += 1
        if any(kw in low for kw in org_keywords):
            orgs_in_props += 1
    elif isinstance(props, dict):
        for v in props.values():
            low = str(v).lower()
            if any(kw in low for kw in role_keywords):
                roles_found += 1
            if any(kw in low for kw in org_keywords):
                orgs_in_props += 1

print(f"\nPeople with role keywords in properties: {roles_found}")
print(f"People with org keywords in properties: {orgs_in_props}")

# Check edges.json for CONNECTED_TO to understand the relationship
with open("edges.json") as f:
    edges = json.load(f)

connected_types = {}
for e in edges:
    if e.get("type") == "CONNECTED_TO":
        props = e.get("properties", {})
        if isinstance(props, dict):
            for k, v in props.items():
                if k not in connected_types:
                    connected_types[k] = set()
                connected_types[k].add(str(v)[:50])

print(f"\nCONNECTED_TO edge property keys: {sorted(connected_types.keys())}")
for k, vals in connected_types.items():
    print(f"  {k}: {list(vals)[:5]}")
