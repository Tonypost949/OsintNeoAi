#!/usr/bin/env python3
import json
from pathlib import Path

NODES_PATH = Path("riconow/Tonypost949-riconow-f7bfe00/AG2OSINTNEOMAXX/nodes.json")
EDGES_PATH = Path("riconow/Tonypost949-riconow-f7bfe00/AG2OSINTNEOMAXX/edges.json")

def main():
    if not NODES_PATH.exists() or not EDGES_PATH.exists():
        print("Database files not found.")
        return
        
    with open(NODES_PATH, "r", encoding="utf-8") as f:
        nodes = json.load(f)
    with open(EDGES_PATH, "r", encoding="utf-8") as f:
        edges = json.load(f)
        
    n_labels = {x['id']: x.get('label', 'UNKNOWN') for x in nodes}
    
    officers = []
    for e in edges:
        s_id = e.get("source_id")
        t_id = e.get("target_id")
        rel_type = e.get("type", "OFFICER_OF")
        
        s_lbl = n_labels.get(s_id, "UNKNOWN")
        t_lbl = n_labels.get(t_id, "UNKNOWN")
        
        if s_lbl == "PERSON" and t_lbl == "ORGANIZATION":
            officers.append((s_id, rel_type, t_id))
        elif s_lbl == "ORGANIZATION" and t_lbl == "PERSON":
            officers.append((t_id, rel_type, s_id))
            
    print("Name,Role,Company")
    for o in sorted(list(set(officers)))[:25]:
        print(f"{o[0]},{o[1]},{o[2]}")

if __name__ == "__main__":
    main()
