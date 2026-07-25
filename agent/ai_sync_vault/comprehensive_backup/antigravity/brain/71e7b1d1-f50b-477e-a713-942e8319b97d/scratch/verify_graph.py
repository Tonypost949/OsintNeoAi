import os
import json

nodes_path = r"c:\Users\HP\OneDrive\Documents\AG2OSINTNEOMAXX\nodes.json"
edges_path = r"c:\Users\HP\OneDrive\Documents\AG2OSINTNEOMAXX\edges.json"

nodes = json.load(open(nodes_path, encoding="utf-8"))
edges = json.load(open(edges_path, encoding="utf-8"))

nodes_size_kb = os.path.getsize(nodes_path) / 1024
edges_size_kb = os.path.getsize(edges_path) / 1024

print(f"Nodes Count: {len(nodes)}")
print(f"Edges Count: {len(edges)}")
print(f"Nodes Size: {nodes_size_kb:.2f} KB ({nodes_size_kb/1024:.2f} MB)")
print(f"Edges Size: {edges_size_kb:.2f} KB ({edges_size_kb/1024:.2f} MB)")

print("\n--- FIRST 20 NODES ---")
print(json.dumps(nodes[:20], indent=2))

print("\n--- FIRST 20 EDGES ---")
print(json.dumps(edges[:20], indent=2))
