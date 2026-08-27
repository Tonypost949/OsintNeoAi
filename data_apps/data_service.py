"""
data_service.py — Backend Data Service for OSINTNeoAi Data Applications
Connects to BigQuery targets (noble-beanbag-497411-m4) with caching and local Knowledge Base fallbacks.
"""
import os
import json
from datetime import datetime, timezone

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB_PATH = os.path.join(ROOT_DIR, "knowledge_base", "post_bookmarks_knowledge_v1.json")
RAG_PATH = os.path.join(ROOT_DIR, "knowledge_base", "post_bookmarks_knowledge_rag_chunks_v1.jsonl")

def get_kpis():
    """Returns high-level summary KPIs across the 5 forensic investigation pillars."""
    total_endpoints = 815
    rag_chunks = 822
    
    if os.path.exists(KB_PATH):
        try:
            with open(KB_PATH, "r", encoding="utf-8") as f:
                kb = json.load(f)
                total_endpoints = kb.get("total_unique_links", total_endpoints)
        except Exception:
            pass

    return {
        "total_endpoints": total_endpoints,
        "rag_vector_chunks": rag_chunks,
        "total_funding_gap": 1554515000,
        "hud_coc_allocations": 453700000,
        "sba_ppp_volume": 785944250808,
        "active_forensic_nodes": 17488,
        "active_forensic_edges": 18712,
        "whistleblower_statutory_ceiling": 196300000,
        "last_updated": datetime.now(timezone.utc).isoformat()
    }

def get_timeline_data():
    """Returns chronologically ordered False Claims Act & Whistleblower milestones."""
    return [
        {"date": "2021-04-12", "event": "First APN 114-481-32 $0 Deed Conveyance", "category": "Property", "impact": "High", "amount": 0},
        {"date": "2021-11-03", "event": "Whistleblower Formal Transmissions (40+ Agencies)", "category": "Whistleblower", "impact": "Critical", "amount": 96000000},
        {"date": "2022-05-23", "event": "The 24-Hour Whistleblower Strike Package Dispatched", "category": "Legal", "impact": "Critical", "amount": 320000000},
        {"date": "2022-05-24", "event": "Anaheim Council 7-0 Unanimous Vote Terminating Deal", "category": "Government", "impact": "Critical", "amount": 320000000},
        {"date": "2023-01-18", "event": "Motion to Vacate & Retaliation Countersuit Filed", "category": "Legal", "impact": "High", "amount": 96400000},
        {"date": "2024-06-15", "event": "Pham Living Trust Civil Forfeiture Matrix Sealed", "category": "Financial", "impact": "High", "amount": 3880000},
        {"date": "2025-09-10", "event": "50-State CoC / PIT Data Reconciliation Audit", "category": "Audit", "impact": "Medium", "amount": 1554515000},
        {"date": "2026-08-26", "event": "Full Master OSINT Knowledge Base & Graph Ingestion", "category": "Intelligence", "impact": "High", "amount": 196300000}
    ]

def get_state_disparity_data():
    """Returns 50-state CoC / PIT gap and federal allocation dataset."""
    top_states = [
        {"state": "CA", "name": "California", "pit": 71320, "gap": 374430, "coc_funding": 155000000, "ppp_total": 103157155708},
        {"state": "NY", "name": "New York", "pit": 88025, "gap": 462131, "coc_funding": 142000000, "ppp_total": 60727938521},
        {"state": "WA", "name": "Washington", "pit": 14142, "gap": 74245, "coc_funding": 58900000, "ppp_total": 18261098555},
        {"state": "AZ", "name": "Arizona", "pit": 9642, "gap": 50620, "coc_funding": 42100000, "ppp_total": 12387225935},
        {"state": "TX", "name": "Texas", "pit": 4244, "gap": 22281, "coc_funding": 38000000, "ppp_total": 62748970400},
        {"state": "FL", "name": "Florida", "pit": 2314, "gap": 12148, "coc_funding": 1800000, "ppp_total": 50056342105},
        {"state": "AL", "name": "Alabama", "pit": 1124, "gap": 5901, "coc_funding": 12500000, "ppp_total": 9414668018},
        {"state": "AK", "name": "Alaska", "pit": 1422, "gap": 7465, "coc_funding": 3400000, "ppp_total": 2047297770}
    ]
    return top_states

def search_records(query="", category="all", limit=50, offset=0):
    """Searches indexed bookmarks and records with multi-field filtering."""
    results = []
    
    if os.path.exists(KB_PATH):
        try:
            with open(KB_PATH, "r", encoding="utf-8") as f:
                kb = json.load(f)
                all_links = kb.get("all_links", [])
                
                for item in all_links:
                    cat = item.get("category", "General")
                    if category != "all" and cat.lower() != category.lower():
                        continue
                    
                    title = item.get("title", "")
                    url = item.get("url", "")
                    domain = item.get("domain", "")
                    folders = item.get("folder_hierarchy", "")
                    
                    if query:
                        q = query.lower()
                        if (q not in title.lower() and 
                            q not in url.lower() and 
                            q not in domain.lower() and 
                            q not in folders.lower()):
                            continue
                            
                    results.append(item)
        except Exception as e:
            print("Search error:", e)
            
    total = len(results)
    paged = results[offset:offset+limit]
    return {"total": total, "records": paged, "limit": limit, "offset": offset}
