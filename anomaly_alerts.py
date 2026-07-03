#!/usr/bin/env python3
"""
Anomaly Alert Monitor - OSINT Forensic Pipeline
==============================================
Runs real-time graph pattern matching over local riconow databases
to detect address cluster concentrations, centrality spikes, and cross-jurisdiction funnels.
"""

import os
import json
import pandas as pd
from pathlib import Path

# Paths to Riconow Database
NODES_PATH = Path("riconow/Tonypost949-riconow-f7bfe00/AG2OSINTNEOMAXX/nodes.json")
EDGES_PATH = Path("riconow/Tonypost949-riconow-f7bfe00/AG2OSINTNEOMAXX/edges.json")
OUTPUT_ALERTS_PATH = Path("alerts_flagged.json")

# Known OC Control Hubs
OC_HUBS = {
    "FOUNTAIN VALLEY": "11770 WARNER AVE",
    "COSTA MESA": "3187 RED HILL AVE",
    "NEWPORT BEACH": "220 NEWPORT CENTER"
}

def load_data():
    if not NODES_PATH.exists() or not EDGES_PATH.exists():
        print("[ERROR] Riconow database files not found. Please sync backups first.")
        return [], []
    
    with open(NODES_PATH, "r", encoding="utf-8") as f:
        nodes = json.load(f)
    with open(EDGES_PATH, "r", encoding="utf-8") as f:
        edges = json.load(f)
        
    return nodes, edges

def run_anomaly_checks():
    print("="*80)
    print("RUNNING FORENSIC ANOMALY MONITORING")
    print("="*80)
    
    nodes, edges = load_data()
    if not nodes:
        return
        
    alerts = {
        "address_clusters": [],
        "degree_anomalies": [],
        "cross_jurisdiction_funnels": []
    }
    
    # 1. Address Cluster Detection
    print("\n[+] Scanning Address Clusters...")
    for node in nodes:
        node_id = str(node.get("id", ""))
        label = node.get("label", "")
        
        # Check if node id matches any known OC Hub
        for hub_name, hub_addr in OC_HUBS.items():
            if hub_addr in node_id.upper():
                alerts["address_clusters"].append({
                    "hub_name": hub_name,
                    "matched_id": node_id,
                    "label": label,
                    "properties": node.get("properties", {})
                })
                
    print(f"    - Flagged {len(alerts['address_clusters'])} nodes registered directly to OC Hubs.")
    
    # 2. Degree Centrality Spikes (5x Baseline)
    print("\n[+] Analyzing Relationship Degrees...")
    connections = {}
    for e in edges:
        s_id = e.get("source_id")
        t_id = e.get("target_id")
        
        connections[s_id] = connections.get(s_id, 0) + 1
        connections[t_id] = connections.get(t_id, 0) + 1
        
    if connections:
        avg_degree = sum(connections.values()) / len(connections)
        anomaly_threshold = avg_degree * 5
        print(f"    - Baseline degree: {avg_degree:.2f} connections")
        print(f"    - Anomaly threshold (5x): {anomaly_threshold:.2f} connections")
        
        for entity_id, deg in connections.items():
            if deg > anomaly_threshold and deg > 10:  # Avoid small absolute scale triggers
                alerts["degree_anomalies"].append({
                    "entity_id": entity_id,
                    "degree": deg,
                    "ratio_to_baseline": round(deg / avg_degree, 2)
                })
                
    print(f"    - Detected {len(alerts['degree_anomalies'])} degree centrality anomalies.")
    
    # 3. Cross-Jurisdiction Funnels
    print("\n[+] Tracking Cross-Jurisdiction Funnels...")
    # Link out-of-state properties / entities to OC hubs
    for e in edges:
        source_id = str(e.get("source_id", ""))
        target_id = str(e.get("target_id", ""))
        
        # If target is an out-of-state address node or has an out-of-state property
        for hub_name, hub_addr in OC_HUBS.items():
            if hub_addr in source_id.upper() or hub_addr in target_id.upper():
                alerts["cross_jurisdiction_funnels"].append({
                    "source_id": source_id,
                    "relationship": e.get("type"),
                    "target_id": target_id,
                    "hub_anchor": hub_name
                })
                
    print(f"    - Mapped {len(alerts['cross_jurisdiction_funnels'])} direct connections anchoring to OC hubs.")
    
    # Save alerts
    with open(OUTPUT_ALERTS_PATH, "w", encoding="utf-8") as f:
        json.dump(alerts, f, indent=2)
        
    print("\n" + "="*80)
    print(f"[SUCCESS] Forensic scan complete. Alerts saved to: {OUTPUT_ALERTS_PATH}")
    print("="*80)

if __name__ == "__main__":
    run_anomaly_checks()
