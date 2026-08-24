import os
import json
import re
from urllib.parse import urlparse
from collections import defaultdict

print("=" * 70)
print("      OSINTNeoAi — MASS CHROME BOOKMARKS INGESTION ENGINE")
print("=" * 70)

base_dir = os.path.dirname(os.path.abspath(__file__))
dump_path = os.path.join(base_dir, "chrome_bookmarks_dump.json")
graph_path = os.path.join(base_dir, "cli", "data", "graph.json")
knowledge_dir = os.path.join(base_dir, "cli", "data", "knowledge")
os.makedirs(knowledge_dir, exist_ok=True)

if not os.path.exists(dump_path):
    print(f"[-] Bookmarks dump not found at {dump_path}")
    exit(1)

with open(dump_path, "r", encoding="utf-8", errors="ignore") as f:
    bookmarks_data = json.load(f)

# Load existing graph
graph_data = {"nodes": [], "edges": []}
if os.path.exists(graph_path):
    try:
        with open(graph_path, "r", encoding="utf-8") as f:
            graph_data = json.load(f)
    except Exception as e:
        print(f"[-] Warning: Failed to load graph: {e}")

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

# Categorization maps
categories = defaultdict(list)
unique_domains = set()
unique_urls = set()
total_bookmarks = 0

# Category rules
def categorize_url(url, name, folder):
    u = url.lower()
    n = name.lower()
    f = folder.lower() if folder else ""
    
    if any(k in u for k in ["geotracker", "waterboards.ca.gov", "edrnet", "lightbox", "envirostor", "phase"]):
        return "Environmental & GeoTracker"
    elif any(k in u for k in ["arcgis", "gis", "parcel", "regrid", "property", "assessor", "land", "map"]):
        return "GIS, Parcels & Maps"
    elif any(k in u for k in ["huntingtonbeachca.gov", "records.", "legistar", "city council", "ocgov", "ochcd"]):
        return "Government & Municipal Portals"
    elif any(k in u for k in ["court", "pacer", "justia", "caselaw", "complaint", "legal", "docket", "referral"]):
        return "Legal & Court Records"
    elif any(k in u for k in ["console.cloud.google.com", "bigquery", "azure", "github", "firebase", "docker"]):
        return "Cloud Infrastructure & DevOps"
    elif any(k in u for k in ["shodan", "dehashed", "osint", "whois", "virustotal", "hunter.io", "intel"]):
        return "OSINT & Cyber Threat Recon"
    elif any(k in u for k in ["mail.google.com", "gmail", "outlook", "drive.google.com"]):
        return "Communications & Cloud Drive"
    else:
        return "General Intelligence"

for profile_name, bms in bookmarks_data.items():
    if not isinstance(bms, list):
        continue
    for b in bms:
        total_bookmarks += 1
        url = b.get("url", "").strip()
        name = b.get("name", "").strip()
        folder = b.get("folder", "").strip()
        
        if not url or url.startswith("javascript:") or url.startswith("chrome://") or url.startswith("about:"):
            continue
        
        unique_urls.add(url)
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain:
            unique_domains.add(domain)
            
        cat = categorize_url(url, name, folder)
        categories[cat].append({
            "profile": profile_name,
            "folder": folder,
            "name": name,
            "url": url,
            "domain": domain
        })

print(f"[+] Processed {total_bookmarks:,} total bookmarks across {len(bookmarks_data)} profiles.")
print(f"[+] Found {len(unique_urls):,} unique URLs across {len(unique_domains):,} distinct domains.")

# Save categorized summaries to knowledge vault
for cat_name, items in categories.items():
    safe_name = cat_name.lower().replace(" ", "_").replace("&", "and").replace(",", "")
    out_file = os.path.join(knowledge_dir, f"bookmarks_{safe_name}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({"category": cat_name, "count": len(items), "bookmarks": items}, f, indent=2)
    print(f" -> [{cat_name}]: {len(items):,} bookmarks saved to {os.path.basename(out_file)}")

# Index high-priority OSINT, Environmental, Legal, and GIS domains into GraphDB
priority_cats = ["Environmental & GeoTracker", "GIS, Parcels & Maps", "Government & Municipal Portals", "Legal & Court Records", "OSINT & Cyber Threat Recon"]

for cat in priority_cats:
    cat_node = add_node("osint.Category", cat)
    seen_in_cat = set()
    for item in categories[cat]:
        d = item["domain"]
        if d and d not in seen_in_cat:
            seen_in_cat.add(d)
            domain_node = add_node("maltego.Domain", d)
            add_edge(cat_node, domain_node, "Contains_Domain")
            
        # Add high-value URLs (GeoTracker IDs, EDR reports, LightBox records)
        if any(k in item["url"].lower() for k in ["t10000", "w0603", "lightbox", "edrnet", "republic"]):
            label = item["name"] or item["url"]
            url_node = add_node("osint.PrimaryEvidenceURL", item["url"])
            add_edge(domain_node, url_node, "Evidence_Link")

# Save GraphDB
with open(graph_path, "w", encoding="utf-8") as f:
    json.dump(graph_data, f, indent=2)

print("\n" + "=" * 70)
print(f"[+] BOOKMARKS INGESTION COMPLETE:")
print(f"    - Total Bookmarks Ingested: {total_bookmarks:,}")
print(f"    - Categories Generated: {len(categories)}")
print(f"    - Updated GraphDB Entities: {len(graph_data['nodes']):,} (+{added_nodes} newly added)")
print(f"    - Updated GraphDB Edges: {len(graph_data['edges']):,} (+{added_edges} newly added)")
print("=" * 70)
