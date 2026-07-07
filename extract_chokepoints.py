#!/usr/bin/env python3
"""
Targeted Choke Point Extractor
==============================
Performs deep graph extraction specifically on the three Orange County address hubs:
1. Fountain Valley Hub (11770 Warner Ave Ste 215)
2. Costa Mesa Hub (3187 Red Hill Ave Ste 213)
3. Newport Beach Hub (220 Newport Center Dr)

Identifies human officers, registered agents, and companies connected directly or
indirectly to these addresses.
"""

import json
from pathlib import Path

NODES_PATH = Path("riconow/Tonypost949-riconow-f7bfe00/AG2OSINTNEOMAXX/nodes.json")
EDGES_PATH = Path("riconow/Tonypost949-riconow-f7bfe00/AG2OSINTNEOMAXX/edges.json")
REPORT_PATH = Path("chokepoint_extraction_report.md")

OC_HUBS = {
    "FOUNTAIN VALLEY HUB": "11770 WARNER AVE",
    "COSTA MESA HUB": "3187 RED HILL AVE",
    "NEWPORT BEACH HUB": "220 NEWPORT CENTER"
}

def load_data():
    if not NODES_PATH.exists() or not EDGES_PATH.exists():
        print("[ERROR] Riconow database files not found.")
        return [], []
    with open(NODES_PATH, "r", encoding="utf-8") as f:
        nodes = json.load(f)
    with open(EDGES_PATH, "r", encoding="utf-8") as f:
        edges = json.load(f)
    return nodes, edges

def run_extraction():
    nodes, edges = load_data()
    if not nodes:
        return
        
    # Index nodes
    node_by_id = {n["id"]: n for n in nodes}
    
    # Track items
    hub_nodes = {name: [] for name in OC_HUBS}
    direct_entities = {name: set() for name in OC_HUBS}
    connected_people = {name: {} for name in OC_HUBS}  # person -> list of roles/entities
    
    # 1. Find all nodes matching the hub address strings
    for nid, node in node_by_id.items():
        nid_upper = str(nid).upper()
        for name, addr in OC_HUBS.items():
            if addr in nid_upper:
                hub_nodes[name].append(nid)
                
    # 2. Track entity links to these hub nodes
    for e in edges:
        source_id = e["source_id"]
        target_id = e["target_id"]
        rel_type = e["type"]
        
        # Check source
        for name, hubs in hub_nodes.items():
            for h_id in hubs:
                if source_id == h_id:
                    direct_entities[name].add((target_id, node_by_id.get(target_id, {}).get("label", "UNKNOWN"), f"Linked via {rel_type}"))
                if target_id == h_id:
                    direct_entities[name].add((source_id, node_by_id.get(source_id, {}).get("label", "UNKNOWN"), f"Linked via {rel_type}"))

    # 3. Find people connected to those entities
    for name, entities in direct_entities.items():
        entity_ids = {ent[0] for ent in entities}
        
        for e in edges:
            source_id = e["source_id"]
            target_id = e["target_id"]
            rel_type = e["type"]
            
            # If a person is linked to one of these entities
            if source_id in entity_ids:
                target_node = node_by_id.get(target_id, {})
                if target_node.get("label") == "PERSON":
                    if target_id not in connected_people[name]:
                        connected_people[name][target_id] = []
                    connected_people[name][target_id].append(f"{rel_type} of {source_id}")
            elif target_id in entity_ids:
                source_node = node_by_id.get(source_id, {})
                if source_node.get("label") == "PERSON":
                    if source_id not in connected_people[name]:
                        connected_people[name][source_id] = []
                    connected_people[name][source_id].append(f"{rel_type} of {target_id}")

    # Generate Markdown Report
    print("[+] Generating choke point extraction report...")
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("# Target Extraction Report: Orange County Choke Points\n\n")
        f.write("This report isolates the human officers, registered agents, and corporate entities structurally anchored in the three high-density registration hubs in Orange County (OC).\n\n")
        
        for name, addr in OC_HUBS.items():
            f.write(f"## {name} (`{addr}`)\n\n")
            
            # Entities section
            f.write("### 🏢 Connected Entities & Properties\n")
            ents = list(direct_entities[name])
            if not ents:
                f.write("*No direct corporate nodes in current subset.*\n\n")
            else:
                f.write("| Entity ID | Type | Relationship |\n")
                f.write("|---|---|---|\n")
                for ent_id, ent_type, rel in sorted(ents)[:20]:  # Limit top 20 to prevent clutter
                    f.write(f"| `{ent_id}` | **{ent_type}** | {rel} |\n")
                if len(ents) > 20:
                    f.write(f"\n*And {len(ents) - 20} more entities...*\n")
                f.write("\n")
                
            # People section
            f.write("### 👥 Associated Human Operators / Agents\n")
            people = connected_people[name]
            if not people:
                f.write("*No human operator nodes linked directly in current subset.*\n\n")
            else:
                f.write("| Person / Operator Name | Relationship & Roles |\n")
                f.write("|---|---|\n")
                for p_name, roles in sorted(people.items())[:20]:
                    roles_str = ", ".join(roles)
                    f.write(f"| **{p_name}** | {roles_str} |\n")
                if len(people) > 20:
                    f.write(f"\n*And {len(people) - 20} more human operators...*\n")
                f.write("\n")
                
            f.write("---\n\n")
            
    print(f"[SUCCESS] Report written to: {REPORT_PATH}")

if __name__ == "__main__":
    run_extraction()
