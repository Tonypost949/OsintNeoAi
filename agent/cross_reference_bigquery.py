"""Deep Entity & Contractor Cross-Referencing Engine across BigQuery & 36,000+ Graph Entities."""

import os
import json
import re
from datetime import datetime, timezone
from typing import List, Dict, Any

TARGET_KEYWORDS = [
    "shea", "woodbridge", "moreno", "srb", "roundtree", "k5", 
    "sidhu", "ament", "flint", "platinum triangle", "angel stadium", "angels",
    "mercy house", "hbnc", "cameron", "11770 warner", "don barnes", "2021102780",
    "irvine", "anaheim", "huntington beach", "viet america society", "andrew do",
    "stewart", "belavita", "pham", "angulo"
]

def run_full_graph_cross_reference():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    results = {
        "matched_nodes": [],
        "matched_edges": [],
        "matched_emails": [],
        "entity_clusters": {},
        "contractor_networks": []
    }
    
    # 1. Search 17,488 nodes.json
    nodes_file = os.path.join(root_dir, "nodes.json")
    if os.path.exists(nodes_file):
        try:
            with open(nodes_file, "r", encoding="utf-8", errors="ignore") as f:
                nodes_list = json.load(f)
                for n in nodes_list:
                    nid = str(n.get("id", "")).lower()
                    nlabel = str(n.get("label", "")).lower()
                    props = str(n.get("properties", {})).lower()
                    
                    matched_kw = [kw for kw in TARGET_KEYWORDS if kw in nid or kw in props]
                    if matched_kw:
                        results["matched_nodes"].append({
                            "id": n.get("id"),
                            "label": n.get("label"),
                            "properties": n.get("properties"),
                            "matched_keywords": matched_kw
                        })
        except Exception as e:
            print(f"Error scanning nodes.json: {e}")

    # 2. Search 18,712 edges.json
    edges_file = os.path.join(root_dir, "edges.json")
    if os.path.exists(edges_file):
        try:
            with open(edges_file, "r", encoding="utf-8", errors="ignore") as f:
                edges_list = json.load(f)
                for e in edges_list:
                    src = str(e.get("source_id", "")).lower()
                    tgt = str(e.get("target_id", "")).lower()
                    etype = str(e.get("type", "")).lower()
                    props = str(e.get("properties", {})).lower()
                    
                    matched_kw = [kw for kw in TARGET_KEYWORDS if kw in src or kw in tgt or kw in props]
                    if matched_kw:
                        results["matched_edges"].append({
                            "source": e.get("source_id"),
                            "target": e.get("target_id"),
                            "relationship": e.get("type"),
                            "source_label": e.get("source_label"),
                            "target_label": e.get("target_label"),
                            "matched_keywords": matched_kw
                        })
        except Exception as e:
            print(f"Error scanning edges.json: {e}")

    # 3. Search Gmail Primary Hits
    gmail_file = os.path.join(root_dir, "data", "gmail_shea_stadium_raw_hits.json")
    if os.path.exists(gmail_file):
        try:
            with open(gmail_file, "r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)
                for item in data:
                    sub = item.get("subject", "").lower()
                    body = item.get("body", "").lower()
                    matched_kw = [kw for kw in TARGET_KEYWORDS if kw in sub or kw in body]
                    if matched_kw:
                        results["matched_emails"].append({
                            "date": item.get("date"),
                            "from": item.get("from"),
                            "to": item.get("to"),
                            "subject": item.get("subject"),
                            "matched_keywords": matched_kw,
                            "preview": item.get("body", "")[:280]
                        })
        except Exception as e:
            print(f"Error scanning gmail hits: {e}")

    # 4. Synthesize Contractor & Entity Clusters
    clusters = {
        "Shea_and_Irvine_Cluster": [],
        "Moreno_and_Stadium_Cluster": [],
        "Anaheim_Cabal_and_Chamber_Cluster": [],
        "MercyHouse_and_HuntingtonBeach_Cluster": [],
        "Healthcare_and_11770Warner_Cluster": []
    }
    
    for n in results["matched_nodes"]:
        nid = n["id"].lower()
        if "shea" in nid or "woodbridge" in nid or "irvine" in nid:
            clusters["Shea_and_Irvine_Cluster"].append(n)
        elif "moreno" in nid or "srb" in nid or "stadium" in nid or "angels" in nid:
            clusters["Moreno_and_Stadium_Cluster"].append(n)
        elif "sidhu" in nid or "ament" in nid or "flint" in nid or "anaheim" in nid:
            clusters["Anaheim_Cabal_and_Chamber_Cluster"].append(n)
        elif "mercy" in nid or "hbnc" in nid or "cameron" in nid or "huntington" in nid:
            clusters["MercyHouse_and_HuntingtonBeach_Cluster"].append(n)
        elif "11770" in nid or "warner" in nid or "angulo" in nid or "pham" in nid or "belavita" in nid:
            clusters["Healthcare_and_11770Warner_Cluster"].append(n)
            
    results["entity_clusters"] = {k: len(v) for k, v in clusters.items()}
    
    # 5. Connect to BigQuery & Catalog
    bq_datasets = []
    try:
        from google.cloud import bigquery
        client = bigquery.Client(project="noble-beanbag-497411-m4")
        datasets = list(client.list_datasets())
        bq_datasets = [d.dataset_id for d in datasets]
    except Exception as e:
        print(f"BQ note: {e}")

    final_report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "FORENSICALLY_SYNTHESIZED",
        "total_nodes_in_master_graph": 17488,
        "total_edges_in_master_graph": 18712,
        "matched_nodes_count": len(results["matched_nodes"]),
        "matched_edges_count": len(results["matched_edges"]),
        "matched_primary_emails_count": len(results["matched_emails"]),
        "cluster_distribution": results["entity_clusters"],
        "bigquery_project": "noble-beanbag-497411-m4",
        "bigquery_datasets": bq_datasets,
        "top_correlated_nodes": results["matched_nodes"][:25],
        "top_correlated_edges": results["matched_edges"][:25],
        "top_correlated_emails": results["matched_emails"][:15]
    }

    out_file = os.path.join(root_dir, "data", "deep_entity_cross_reference_report.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(final_report, f, indent=2, ensure_ascii=False)
        
    print(f"\n[✓] Cross-Referencing Complete!")
    print(f"    • Matched Nodes:  {len(results['matched_nodes']):,}")
    print(f"    • Matched Edges:  {len(results['matched_edges']):,}")
    print(f"    • Matched Emails: {len(results['matched_emails']):,}")
    print(f"    • Output Saved:   {out_file}")
    
    return final_report

if __name__ == "__main__":
    run_full_graph_cross_reference()
