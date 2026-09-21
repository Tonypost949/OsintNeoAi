import json
import os
import networkx as nx
import time

nodes_path = r"C:\OsintNeoAi\nodes.json"
edges_path = r"C:\OsintNeoAi\edges.json"

print("Loading 18,989 nodes and 20,212 edges into NetworkX graph solver...")

with open(nodes_path, "r", encoding="utf-8") as f:
    nodes_data = json.load(f)
with open(edges_path, "r", encoding="utf-8") as f:
    edges_data = json.load(f)

G = nx.Graph()

# Add nodes with attributes
for n in nodes_data:
    nid = n.get("id") or n.get("node_id") or n.get("name")
    if nid:
        G.add_node(nid, label=n.get("label", nid), type=n.get("type", "UNKNOWN"))

# Add edges with attributes
for e in edges_data:
    src = e.get("source") or e.get("from") or e.get("source_id")
    tgt = e.get("target") or e.get("to") or e.get("target_id")
    if src and tgt:
        G.add_edge(src, tgt, relationship=e.get("relationship", "CONNECTED"))

print(f"NetworkX Graph Built: {G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges")

# Compute Degree Centrality
degree_centrality = nx.degree_centrality(G)
top_degree = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:20]

# Format centrality report
top_degree_nodes = []
for node_id, score in top_degree:
    node_attr = G.nodes[node_id]
    top_degree_nodes.append({
        "node_id": node_id,
        "label": node_attr.get("label"),
        "type": node_attr.get("type"),
        "degree_centrality": round(score, 6),
        "degree_count": G.degree(node_id)
    })

payload = {
    "report_name": "Master OSINT Entity Graph Centrality & Hub Identification Report",
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    "total_nodes": G.number_of_nodes(),
    "total_edges": G.number_of_edges(),
    "top_degree_hubs": top_degree_nodes
}

out1 = r"C:\OsintNeoAi\data\graph_centrality_report.json"
out2 = r"C:\OsintNeoAi\public\graph_centrality_report.json"

with open(out1, "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2)

with open(out2, "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2)

print(f"Successfully calculated graph centrality for {G.number_of_nodes():,} nodes and saved report to {out1} and {out2}")
