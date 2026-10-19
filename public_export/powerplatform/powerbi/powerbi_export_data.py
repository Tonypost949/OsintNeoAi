import json
import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

print("[*] Generating Power BI Forensic Data Model...")

nodes_file = os.path.join(ROOT_DIR, "nodes.json")
edges_file = os.path.join(ROOT_DIR, "edges.json")

if os.path.exists(nodes_file):
    with open(nodes_file, "r", encoding="utf-8") as f:
        nodes = json.load(f)
    
    out_nodes = os.path.join(BASE_DIR, "powerbi_nodes.csv")
    with open(out_nodes, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["NodeID", "Label", "Name", "City", "Address", "LastSaleValue", "RiskCategory"])
        for n in nodes:
            nid = n.get("id", "")
            lbl = n.get("label", "")
            props = n.get("properties", {})
            name = props.get("name", nid)
            city = props.get("city", "")
            addr = props.get("address", "")
            sale = props.get("last_sale_value", "")
            
            # Categorize
            risk = "Standard"
            if any(k in name.lower() for k in ["hospice", "care", "palliative", "clinic"]):
                risk = "Healthcare Shell"
            elif "edison" in name.lower():
                risk = "Utility Grantor"
            elif "pham" in name.lower() or "do" in name.lower():
                risk = "Target Trust/Officer"
                
            writer.writerow([nid, lbl, name, city, addr, sale, risk])
    print(f"[+] Wrote {len(nodes):,} nodes to {out_nodes}")

if os.path.exists(edges_file):
    with open(edges_file, "r", encoding="utf-8") as f:
        edges = json.load(f)
    
    out_edges = os.path.join(BASE_DIR, "powerbi_edges.csv")
    with open(out_edges, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["SourceID", "SourceLabel", "Relationship", "TargetID", "TargetLabel", "Role", "Date"])
        for e in edges:
            s_id = e.get("source_id") or e.get("source", "")
            s_lbl = e.get("source_label", "")
            rel = e.get("type", "")
            t_id = e.get("target_id") or e.get("target", "")
            t_lbl = e.get("target_label", "")
            props = e.get("properties", {})
            role = props.get("role", "")
            dt = props.get("date", "")
            writer.writerow([s_id, s_lbl, rel, t_id, t_lbl, role, dt])
    print(f"[+] Wrote {len(edges):,} edges to {out_edges}")

print("[+] Power BI Data Model Export Complete.")
