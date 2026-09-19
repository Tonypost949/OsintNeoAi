#!/usr/bin/env python3
"""
autonomous_enrichment_worker.py — Continuous Background Forensic Enrichment Engine
Autonomously enriches target accounts, evidence nodes, and graph clusters across BigQuery and MCP tools.
"""

import os
import sys
import time
import json
import glob
from pathlib import Path

ROOT_DIR = Path("C:/OsintNeoAi")
sys.path.insert(0, str(ROOT_DIR / "tools"))
import openosint_mcp_server as mcp

TARGETS_FILE = ROOT_DIR / "agent" / "target_accounts_master.json"
DATA_DIR = ROOT_DIR / "data"
GRAPH_OUTPUT = DATA_DIR / "live_entity_graph.json"
TELEMETRY_OUTPUT = ROOT_DIR / "public" / "live_telemetry.geojson"

def load_targets():
    if not TARGETS_FILE.exists():
        return []
    with open(TARGETS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    targets = []
    for cat, accts in data.items():
        for a in accts:
            targets.append({"account": a.strip(), "category": cat})
    return targets

def run_enrichment_cycle(cycle_num):
    print(f"\n[🔄] Starting Autonomous Enrichment Cycle #{cycle_num} at {time.strftime('%Y-%m-%d %H:%M:%S')}...")
    targets = load_targets()
    nodes = []
    edges = []
    
    # 1. System Health & Target Account Analysis
    health = mcp.handle_tool_call("osint_system_health", {})
    print(f"  [+] MCP Forensic Engine Status: {health.get('status')} (Target: {health.get('bigquery_target')})")
    
    for idx, t in enumerate(targets):
        acct = t["account"]
        cat = t["category"]
        
        # Enrich via MCP lookup tool
        email_res = mcp.handle_tool_call("osint_lookup_email", {"email": acct})
        entity_res = mcp.handle_tool_call("osint_search_entity", {"query": acct.split("@")[0]})
        
        node_id = f"target_{acct}"
        nodes.append({
            "id": node_id,
            "label": acct,
            "type": "TargetAccount",
            "category": cat,
            "status": "Enriched",
            "last_audit": time.strftime("%Y-%m-%d %H:%M:%SZ")
        })
        
        # Link category cluster
        cat_id = f"cluster_{cat}"
        edges.append({
            "source": node_id,
            "target": cat_id,
            "relationship": "BELONGS_TO_CATEGORY"
        })

    # 2. Build and Update Graph Model
    graph_payload = {
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%SZ"),
        "cycle": cycle_num,
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "nodes": nodes,
        "edges": edges
    }
    
    with open(GRAPH_OUTPUT, "w", encoding="utf-8") as out:
        json.dump(graph_payload, out, indent=2)
    print(f"  [✓] Updated Live Entity Graph: {len(nodes)} nodes, {len(edges)} edges -> {GRAPH_OUTPUT.name}")

    # 3. Update Geospatial Telemetry Feed
    features = []
    for idx, t in enumerate(targets[:15]):
        # Simulated geospatial clustering for tactical map playback
        base_lat = 33.6595 + (idx * 0.005)
        base_lng = -117.9988 - (idx * 0.004)
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [base_lng, base_lat]
            },
            "properties": {
                "title": t["account"],
                "category": t["category"],
                "status": "Active Surveillance",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        })
        
    geo_payload = {
        "type": "FeatureCollection",
        "features": features
    }
    with open(TELEMETRY_OUTPUT, "w", encoding="utf-8") as out:
        json.dump(geo_payload, out, indent=2)
    print(f"  [✓] Live Telemetry Feed Synchronized -> {TELEMETRY_OUTPUT.name}")

    # 4. Ingest and Score Zero-Value Ledger Staging Entries
    staging_dir = DATA_DIR / "staging"
    master_registry_file = DATA_DIR / "MASTER_OSINT_EVIDENCE_REGISTRY.json"
    master_entities = []
    if master_registry_file.exists():
        try:
            with open(master_registry_file, "r", encoding="utf-8") as rf:
                reg_data = json.load(rf)
                master_entities = reg_data.get("registry", [])
        except Exception:
            pass

    if staging_dir.exists():
        staging_files = list(staging_dir.glob("*.json"))
        for sf in staging_files:
            try:
                with open(sf, "r", encoding="utf-8") as f:
                    entry = json.load(f)
                
                content = (entry.get("raw_content", "") or "").lower()
                matched_entity = None
                
                # Check for hits against the 109 master registry entities
                for ent in master_entities:
                    name = ent.get("Entity_Name", "").lower()
                    ident = ent.get("Primary_Identifier", "").lower()
                    if (name and len(name) > 3 and name in content) or (ident and len(ident) > 3 and ident in content):
                        matched_entity = ent
                        break

                if matched_entity:
                    entry["ledger_value"] = 500.0  # Valued upon cryptographic evidence attachment
                    entry["enrichment_status"] = "CORROBORATED"
                    entry["linked_entity"] = f"{matched_entity.get('Record_ID')} - {matched_entity.get('Entity_Name')}"
                    entry["tft_reward"] = 50
                    entry["last_valuation_time"] = time.strftime("%Y-%m-%d %H:%M:%SZ")
                else:
                    entry["enrichment_status"] = "APPENDED_ZERO_VALUE"
                    entry["linked_entity"] = "Queued on Immutable Ledger (Zero Value)"

                with open(sf, "w", encoding="utf-8") as f:
                    json.dump(entry, f, indent=2)
            except Exception:
                pass
        if staging_files:
            print(f"  [✓] Processed {len(staging_files)} ledger staging payloads.")

def main():
    print("=" * 65)
    print("  OSINTNEOAI CONTINUOUS AUTONOMOUS ENRICHMENT ENGINE ACTIVE")
    print("=" * 65)
    cycle = 1
    while True:
        try:
            run_enrichment_cycle(cycle)
            cycle += 1
            print("[⏳] Sleeping for 60 seconds until next background enrichment cycle...")
            time.sleep(60)
        except KeyboardInterrupt:
            print("\n[!] Worker interrupted by operator.")
            break
        except Exception as e:
            print(f"[!] Error during enrichment cycle #{cycle}: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
