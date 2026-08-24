import os
import json
import requests
import re
from bs4 import BeautifulSoup

print("=" * 70)
print("      OSINTNeoAi — KALI LINUX OSINT & FORENSIC SUITE INGESTION")
print("=" * 70)

base_dir = os.path.dirname(os.path.abspath(__file__))
tools_file = os.path.join(base_dir, "cli", "data", "tools.json")
graph_path = os.path.join(base_dir, "cli", "data", "graph.json")
knowledge_file = os.path.join(base_dir, "cli", "data", "knowledge", "learned_kali_linux.txt")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
}

# 1. Fetch Kali Tools Main Index
print("[*] Fetching Kali Linux tools catalog from https://www.kali.org/tools/ ...")
r = requests.get('https://www.kali.org/tools/', headers=headers, timeout=15)
soup = BeautifulSoup(r.text, 'html.parser')

kali_tools = []
seen_names = set()

# Curated high-value categories
category_map = {
    "osint": "OSINT & Intelligence Gathering",
    "recon": "Network & Reconnaissance",
    "dns": "DNS & Domain Enumeration",
    "web": "Web Application & Directory Fuzzing",
    "forensics": "Digital Forensics & Incident Response",
    "crypto": "Password Auditing & Cryptanalysis",
    "wireless": "Wireless & RF Intelligence",
    "exploit": "Exploitation & Vulnerability Assessment",
    "sniff": "Packet Sniffing & Traffic Analysis"
}

# Extract tools from kali.org/tools/
for a in soup.find_all('a', href=True):
    href = a['href']
    name = a.get_text(strip=True)
    if 'kali.org/tools/' in href and '#' in href and name and name not in seen_names and not name.startswith('$'):
        seen_names.add(name)
        
        # Categorize
        cat = "General Kali Tools"
        n_lower = name.lower()
        if any(k in n_lower for k in ["harvester", "spiderfoot", "amass", "sherlock", "photon", "metagoofil", "instaloader", "linkedin", "tookie", "osint"]):
            cat = "OSINT & Social Intelligence"
        elif any(k in n_lower for k in ["dns", "sublist3r", "assetfinder", "findomain", "massdns", "dnswalk"]):
            cat = "DNS & Subdomain Recon"
        elif any(k in n_lower for k in ["nmap", "unicorn", "dmitry", "legion", "autorecon"]):
            cat = "Network & Host Discovery"
        elif any(k in n_lower for k in ["dirb", "gobuster", "ffuf", "feroxbuster", "dirsearch", "burp", "zap", "nikto", "wpscan"]):
            cat = "Web Application & Asset Discovery"
        elif any(k in n_lower for k in ["volatility", "autopsy", "foremost", "binwalk", "sleuth", "bulk_extractor", "exiftool", "pdf"]):
            cat = "Digital Forensics & Metadata"
        elif any(k in n_lower for k in ["hashcat", "john", "hydra", "medusa", "ophcrack"]):
            cat = "Credential & Hash Analysis"
        elif any(k in n_lower for k in ["wireshark", "tcpdump", "ettercap", "bettercap", "responder", "mitm"]):
            cat = "Traffic Interception & Analysis"
        else:
            cat = "Kali Linux Tool Suite"
            
        kali_tools.append({
            "name": name,
            "category": cat,
            "description": f"Kali Linux security & OSINT utility: {name}",
            "url": href if href.startswith('http') else f"https://www.kali.org{href}"
        })

print(f"[+] Extracted {len(kali_tools)} Kali Linux tools and utilities.")

# 2. Add to data/tools.json
existing_tools_data = {"tools": []}
if os.path.exists(tools_file):
    try:
        with open(tools_file, "r", encoding="utf-8") as f:
            existing_tools_data = json.load(f)
    except Exception:
        pass

existing_names = {t.get("name", "").lower() for t in existing_tools_data.get("tools", [])}
added_tools = 0
for kt in kali_tools:
    if kt["name"].lower() not in existing_names:
        existing_tools_data["tools"].append(kt)
        existing_names.add(kt["name"].lower())
        added_tools += 1

with open(tools_file, "w", encoding="utf-8") as f:
    json.dump(existing_tools_data, f, indent=2)

print(f"[+] Updated data/tools.json: {added_tools} new Kali tools added. (Total catalog: {len(existing_tools_data['tools'])} tools)")

# 3. Update GraphDB with Kali Categories and Tools
graph_data = {"nodes": [], "edges": []}
if os.path.exists(graph_path):
    try:
        with open(graph_path, "r", encoding="utf-8") as f:
            graph_data = json.load(f)
    except Exception:
        pass

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

kali_root = add_node("osint.Framework", "Kali Linux Security Suite")

for kt in kali_tools:
    cat_node = add_node("osint.Category", kt["category"])
    add_edge(kali_root, cat_node, "Contains_Category")
    tool_node = add_node("osint.Tool", kt["name"])
    add_edge(cat_node, tool_node, "Includes_Tool")
    url_node = add_node("osint.ToolURL", kt["url"])
    add_edge(tool_node, url_node, "Documentation_URL")

with open(graph_path, "w", encoding="utf-8") as f:
    json.dump(graph_data, f, indent=2)

print(f"[+] GraphDB Updated: +{added_nodes} nodes, +{added_edges} edges. (Total: {len(graph_data['nodes'])} nodes, {len(graph_data['edges'])} edges)")

# 4. Save Knowledge Digest
knowledge_text = f"""Source: https://www.kali.org/tools/
----------------------------------------
KALI LINUX OSINT & SECURITY TOOL SUITE
Total Tools Cataloged: {len(kali_tools)}

CATEGORIES & INVENTORY:
"""
cats = {}
for kt in kali_tools:
    cats.setdefault(kt["category"], []).append(kt)

for cat_name, tools in cats.items():
    knowledge_text += f"\n### {cat_name} ({len(tools)} tools)\n"
    for t in tools:
        knowledge_text += f"- {t['name']}: {t['url']}\n"

with open(knowledge_file, "w", encoding="utf-8") as f:
    f.write(knowledge_text)

print(f"[+] Saved comprehensive Kali knowledge digest to {knowledge_file}")
print("=" * 70)
