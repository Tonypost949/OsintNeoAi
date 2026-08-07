"""Check PPP loan data for embedded officer names."""
import json

with open("nodes.json") as f:
    nodes = json.load(f)
with open("edges.json") as f:
    edges = json.load(f)

# Show a few PPP_LOAN nodes
ppp_nodes = [n for n in nodes if n.get("label") == "PPP_LOAN"]
print(f"PPP_LOAN nodes: {len(ppp_nodes)}")
if ppp_nodes:
    for n in ppp_nodes[:3]:
        print(f"\n  Node: {json.dumps(n, indent=2)[:500]}")

# Show RECEIVED_PPP edges
ppp_edges = [e for e in edges if e.get("type") == "RECEIVED_PPP"]
print(f"\nRECEIVED_PPP edges: {len(ppp_edges)}")
if ppp_edges:
    for e in ppp_edges[:3]:
        print(f"\n  Edge: {json.dumps(e, indent=2)[:300]}")
