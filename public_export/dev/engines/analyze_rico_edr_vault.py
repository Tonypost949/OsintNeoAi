import os
import json
import re

print("=" * 70)
print("   OSINTNeoAi — EDR & RICO MASTER CORRELATION PIPELINE")
print("=" * 70)

base_dir = os.path.dirname(os.path.abspath(__file__))
graph_path = os.path.join(base_dir, "cli", "data", "graph.json")

# 1. Load Existing Graph
graph_data = {"nodes": [], "edges": []}
if os.path.exists(graph_path):
    try:
        with open(graph_path, "r", encoding="utf-8") as f:
            graph_data = json.load(f)
    except Exception as e:
        print(f"[-] Failed to load existing graph: {e}")

existing_node_vals = {n.get("value") for n in graph_data.get("nodes", [])}
added_nodes = 0
added_edges = 0

def add_node(entity_type, value):
    global added_nodes
    if value and value not in existing_node_vals:
        node_id = f"node_{len(graph_data['nodes']) + 1}"
        graph_data["nodes"].append({"id": node_id, "type": entity_type, "value": value})
        existing_node_vals.add(value)
        added_nodes += 1
        return node_id
    for n in graph_data["nodes"]:
        if n.get("value") == value:
            return n.get("id")
    return None

def add_edge(source_id, target_id, relation_type):
    global added_edges
    if source_id and target_id:
        edge = {"source": source_id, "target": target_id, "type": relation_type}
        graph_data.setdefault("edges", []).append(edge)
        added_edges += 1

# 2. Ingest EDR Datasets
edr_files = [
    os.path.join(base_dir, "edr_all_gps_coordinates.json"),
    os.path.join(base_dir, "edr_gps_mapping_clean.json"),
    os.path.join(base_dir, "edr_masked_address_log.json")
]

edr_count = 0
for ef in edr_files:
    if os.path.exists(ef):
        try:
            with open(ef, "r", encoding="utf-8") as f:
                data = json.load(f)
                items = data if isinstance(data, list) else data.get("records", [])
                for item in items:
                    addr = item.get("cover_address") or item.get("address")
                    file_ref = item.get("file")
                    lat = item.get("latitude")
                    lon = item.get("longitude")
                    real_loc = item.get("real_physical_location")
                    
                    if addr and len(str(addr).strip()) > 3:
                        addr_clean = str(addr).replace("\n", " ").strip()
                        n_addr = add_node("edr.Address", addr_clean)
                        edr_count += 1
                        
                        if file_ref:
                            n_file = add_node("edr.Document", file_ref)
                            add_edge(n_addr, n_file, "Documented_In")
                        if real_loc and real_loc not in ["Unknown / Map Coordinates", "Not listed in PDF text"]:
                            n_loc = add_node("edr.PhysicalLocation", real_loc)
                            add_edge(n_addr, n_loc, "Resolved_Location")
                        if lat and lon and lat != "N/A" and lon != "N/A":
                            n_coord = add_node("edr.Coordinates", f"{lat},{lon}")
                            add_edge(n_addr, n_coord, "Geolocated_At")
        except Exception as e:
            print(f"[-] Error processing {ef}: {e}")

print(f"[+] Ingested EDR records: {edr_count} address references parsed.")

# 3. Ingest RICO Evidence Matrix & GIS Layer Entities
gis_file = os.path.join(base_dir, "hbnc_rico_gis.html")
if os.path.exists(gis_file):
    try:
        with open(gis_file, "r", encoding="utf-8") as f:
            html_text = f.read()
            parcels = re.findall(r"['\"]name['\"]\s*:\s*['\"]([^'\"]+)['\"]", html_text)
            for p in parcels:
                add_node("rico.Parcel", p)
            
            llcs = set(re.findall(r"\b[A-Z0-9\s]{3,30}\sLLC\b", html_text, re.IGNORECASE))
            for llc in llcs:
                n_llc = add_node("rico.ShellLLC", llc.strip())
                add_edge(n_llc, add_node("rico.Network", "HBNC_RICO_Corridor"), "Affiliated_With")
            print(f"[+] Extracted {len(parcels)} GIS Parcels and {len(llcs)} Shell LLCs from RICO GIS.")
    except Exception as e:
        print(f"[-] Error reading RICO GIS: {e}")

# 4. Ingest Evidence Matrix Entities
evidence_matrix_file = os.path.join(base_dir, "EVIDENCE_MATRIX.md")
if os.path.exists(evidence_matrix_file):
    try:
        with open(evidence_matrix_file, "r", encoding="utf-8") as f:
            em_text = f.read()
            targets = re.findall(r"\|\s*([A-Z0-9\-_]+)\s*\|\s*([^\|]+)\|", em_text)
            for t_id, t_desc in targets:
                if t_id != "ID" and "---" not in t_id:
                    n_tgt = add_node("rico.EvidenceItem", f"[{t_id.strip()}] {t_desc.strip()}")
            print(f"[+] Extracted {len(targets)} Evidence items from EVIDENCE_MATRIX.md.")
    except Exception as e:
        print(f"[-] Error reading EVIDENCE_MATRIX: {e}")

# 5. Save Updated GraphDB
os.makedirs(os.path.dirname(graph_path), exist_ok=True)
with open(graph_path, "w", encoding="utf-8") as f:
    json.dump(graph_data, f, indent=2)

print("\n" + "-" * 70)
print(f"[+] GRAPHDB UPDATE COMPLETE:")
print(f"    - Total Nodes in Graph: {len(graph_data['nodes'])} (+{added_nodes} newly added)")
print(f"    - Total Edges in Graph: {len(graph_data['edges'])} (+{added_edges} newly added)")
print(f"    - Graph saved to: {graph_path}")
print("=" * 70)
