import json
import os

GRAPH_FILE = "cli/data/cases/nworico.json"

def load_graph():
    if os.path.exists(GRAPH_FILE):
        with open(GRAPH_FILE, "r") as f:
            return json.load(f)
    return {"nodes": [], "edges": []}

def save_graph(data):
    os.makedirs(os.path.dirname(GRAPH_FILE), exist_ok=True)
    with open(GRAPH_FILE, "w") as f:
        json.dump(data, f, indent=4)

def inject_evidence_cluster():
    graph = load_graph()
    
    new_nodes = [
        {"id": "person-victor-nunez", "label": "Victor Nunez", "type": "maltego.Person", "properties": {"Role": "Assistant Community Manager", "Company": "Shea Properties"}},
        {"id": "person-carissa-doyle", "label": "Carissa Doyle", "type": "maltego.Person", "properties": {"Role": "Leasing Specialist", "Company": "Shea Properties"}},
        {"id": "doc-15-day-notice", "label": "15 Day Notice (March 2021)", "type": "maltego.Document", "properties": {"Status": "Suppressed / Late Delivery"}},
        {"id": "doc-eviction-restoration", "label": "Eviction Restoration (Aug 4 2021)", "type": "maltego.Document", "properties": {"Status": "Withheld until Aug 19"}}
    ]
    
    new_edges = [
        {"source": "person-victor-nunez", "target": "shea-properties", "label": "WORKS_FOR"},
        {"source": "person-carissa-doyle", "target": "shea-properties", "label": "WORKS_FOR"},
        {"source": "person-victor-nunez", "target": "doc-15-day-notice", "label": "SENT_VIA_EMAIL"},
        {"source": "person-victor-nunez", "target": "doc-eviction-restoration", "label": "WITHHELD_AND_LATER_SENT"},
        {"source": "doc-eviction-restoration", "target": "loc-212-southbrook", "label": "APPLIES_TO"},
        {"source": "doc-15-day-notice", "target": "loc-212-southbrook", "label": "APPLIES_TO"}
    ]
    
    existing_node_ids = {node["id"] for node in graph.get("nodes", [])}
    for node in new_nodes:
        if node["id"] not in existing_node_ids:
            graph["nodes"].append(node)
            
    graph["edges"].extend(new_edges)
    save_graph(graph)
    print(f"✅ Injected {len(new_nodes)} nodes and {len(new_edges)} edges into {GRAPH_FILE}.")

if __name__ == "__main__":
    inject_evidence_cluster()
