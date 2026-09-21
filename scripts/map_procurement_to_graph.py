import json
import os
import shutil
import time

nodes_path = r"C:\OsintNeoAi\nodes.json"
edges_path = r"C:\OsintNeoAi\edges.json"
procurement_json = r"C:\OsintNeoAi\data\oc_procurement_1500_bids_ocr.json"

# Pre-action reversible backup
backup_dir = r"C:\OsintNeoAi\backups\graph_procurement_backup"
os.makedirs(backup_dir, exist_ok=True)
if os.path.exists(nodes_path):
    shutil.copy(nodes_path, os.path.join(backup_dir, "nodes.json"))
if os.path.exists(edges_path):
    shutil.copy(edges_path, os.path.join(backup_dir, "edges.json"))

print("Backed up pre-existing nodes.json and edges.json")

# Read procurement bids
with open(procurement_json, "r", encoding="utf-8") as f:
    proc_data = json.load(f)

bids = proc_data.get("bids", [])
print(f"Mapping {len(bids):,} bids to network graph...")

# Read existing graph
nodes = []
edges = []
if os.path.exists(nodes_path):
    with open(nodes_path, "r", encoding="utf-8") as f:
        nodes = json.load(f)
if os.path.exists(edges_path):
    with open(edges_path, "r", encoding="utf-8") as f:
        edges = json.load(f)

# Add primary entity node
oc_gov_id = "GOV-OC-PROCUREMENT"
nodes.append({
    "id": oc_gov_id,
    "label": "County of Orange Procurement Office",
    "type": "GOVERNMENT_AGENCY",
    "category": "Municipal Procurement Portal",
    "jurisdiction": "Orange County, CA"
})

# Add 1,500 bid nodes and edges
added_nodes = 1
added_edges = 0

for b in bids:
    bid_id = f"BID-{b['bid_sequence_id']:04d}"
    nodes.append({
        "id": bid_id,
        "label": f"{b['bid_identifier']} (OC Solicitation)",
        "type": "PROCUREMENT_SOLICITATION",
        "agency": oc_gov_id,
        "ocr_confidence": b.get("ocr_confidence", 0.992)
    })
    added_nodes += 1

    edges.append({
        "id": f"EDGE-PROC-{b['bid_sequence_id']:04d}",
        "source": oc_gov_id,
        "target": bid_id,
        "relationship": "ISSUED_SOLICITATION",
        "timestamp": time.strftime("%Y-%m-%d")
    })
    added_edges += 1

# Save updated graph
with open(nodes_path, "w", encoding="utf-8") as f:
    json.dump(nodes, f, indent=2)

with open(edges_path, "w", encoding="utf-8") as f:
    json.dump(edges, f, indent=2)

# Copy to public folder
pub_nodes = r"C:\OsintNeoAi\public\nodes.json"
pub_edges = r"C:\OsintNeoAi\public\edges.json"
shutil.copy(nodes_path, pub_nodes)
shutil.copy(edges_path, pub_edges)

print(f"Successfully mapped {added_nodes:,} nodes and {added_edges:,} edges into graph tables!")
print(f"Total Graph Volume: {len(nodes):,} nodes, {len(edges):,} edges")
