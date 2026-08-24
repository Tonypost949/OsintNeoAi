import argparse
import sys
import threading
from core.entities import Domain, Email, Person, IPAddress, SocialProfile
from core.transforms import AVAILABLE_TRANSFORMS
from core.graph_db import GraphDB
from core.trx_executor import LocalTRXExecutor

# Simulated in-memory database of found entities
investigation_graph = []
db = GraphDB()
trx = LocalTRXExecutor()

def investigate(args):
    print(f"[*] Starting investigation on {args.type}: {args.value}")
    entity = None
    if args.type.lower() == "domain":
        entity = Domain(value=args.value)
    elif args.type.lower() == "email":
        entity = Email(value=args.value)
    else:
        print(f"[-] Unsupported entity type: {args.type}")
        return

    investigation_graph.append(entity)
    print(f"[+] Added to graph: {entity}")

def run_transform(args):
    transform_name = args.transform.lower()
    if transform_name not in AVAILABLE_TRANSFORMS:
        print(f"[-] Unknown transform: {args.transform}")
        return

    transform = AVAILABLE_TRANSFORMS[transform_name]
    
    # For demo, we just create a dummy entity to feed it based on the target value.
    # Ideally we would look up an existing entity by ID.
    # Let's infer type from transform name roughly.
    if "domain" in transform_name:
        target_entity = Domain(value=args.target)
    elif "email" in transform_name:
        target_entity = Email(value=args.target)
    elif "ip" in transform_name:
        target_entity = IPAddress(value=args.target)
    elif "person" in transform_name:
        target_entity = Person(value=args.target)
    else:
        target_entity = Domain(value=args.target)

    print(f"[*] Running {transform.name} on {target_entity}")
    results = transform.run(target_entity)
    
    if results:
        for r in results:
            investigation_graph.append(r)
            print(f"[+] Found new entity: {r}")
    else:
        print("[-] No results found.")

def report(args):
    print("\n--- Investigation Report ---")
    db.load()
    nodes = db.data.get("nodes", [])
    edges = db.data.get("edges", []) if len(db.data.get("edges", [])) >= len(db.data.get("links", [])) else db.data.get("links", [])
    if nodes:
        print(f"Total Persistent Graph Entities: {len(nodes)}")
        print(f"Total Graph Relations/Edges: {len(edges)}")
        print("\n--- Discovered Entities (Sample) ---")
        for e in nodes[:40]:
            print(f"  - [{e.get('type')}] {e.get('value')}")
        if len(nodes) > 40:
            print(f"  ... and {len(nodes) - 40} more entities in data/graph.json")
    elif not investigation_graph:
        print("No entities found. The graph is empty.")
    else:
        print(f"Total session entities: {len(investigation_graph)}")
        for e in investigation_graph:
            print(f"  - {e}")
    print("----------------------------\n")

def learn(args):
    import os
    import requests
    import hashlib

    source = args.source
    content = ""
    
    if source.startswith("http://") or source.startswith("https://"):
        print(f"[*] Fetching material from {source}...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        try:
            response = requests.get(source, headers=headers, timeout=15)
            response.raise_for_status()
            content = response.text
            
            # Special handling for Start.me dashboards
            if "start.me/p/" in source:
                import re
                import json
                print("[*] Detecting Start.me OSINT dashboard. Fetching structured widget payload...")
                slug_match = re.search(r"start\.me/p/([a-zA-Z0-9_-]+)", source)
                if slug_match:
                    slug = slug_match.group(1)
                    api_url = f"https://api.start.me/p/{slug}"
                    api_headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Accept': 'application/json',
                        'Origin': 'https://start.me',
                        'Referer': 'https://start.me/'
                    }
                    try:
                        api_res = requests.get(api_url, headers=api_headers, timeout=15)
                        if api_res.status_code == 200:
                            api_data = api_res.json()
                            columns = api_data.get('page', {}).get('columns', [])
                            tools_file = "data/tools.json"
                            existing_tools = {"tools": []}
                            if os.path.exists(tools_file):
                                try:
                                    with open(tools_file, "r", encoding="utf-8") as f:
                                        existing_tools = json.load(f)
                                except Exception:
                                    pass
                            
                            existing_names = {t.get("name", "").lower() for t in existing_tools.get("tools", [])}
                            added = 0
                            parsed_summary = []
                            
                            for col in columns:
                                for w in col.get('widgets', []):
                                    sec_title = w.get('title', 'OSINT Tools').strip() or "General Tools"
                                    items = w.get('items', {})
                                    links = items.get('links', []) if isinstance(items, dict) else []
                                    for l in links:
                                        t_title = (l.get('title') or "").strip()
                                        t_url = (l.get('url') or "").strip()
                                        t_desc = (l.get('description') or "").strip()
                                        if t_title and t_url and t_title.lower() not in existing_names:
                                            existing_tools["tools"].append({
                                                "name": t_title,
                                                "category": sec_title,
                                                "description": t_desc or f"OSINT resource under {sec_title}",
                                                "url": t_url
                                            })
                                            existing_names.add(t_title.lower())
                                            added += 1
                                            parsed_summary.append(f"[{sec_title}] {t_title}: {t_url}")
                            
                            if added > 0:
                                with open(tools_file, "w", encoding="utf-8") as f:
                                    json.dump(existing_tools, f, indent=2)
                                print(f"[+] Successfully extracted {added} OSINT tools into data/tools.json across {len(columns)} columns!")
                            content = f"Nixintel OSINT Resource List Dashboard ({source})\nTotal Tools Extracted: {len(parsed_summary)}\n\n" + "\n".join(parsed_summary)
                    except Exception as e:
                        print(f"[-] Failed to fetch structured Start.me API: {e}")
            
            # Special handling for Claude artifacts
            if "claude.ai/public/artifacts/" in source:
                import re
                import json
                print("[*] Detecting Claude artifact. Attempting to extract OSINT tools...")
                pattern = re.compile(r"\{cat:'(.*?)',name:'(.*?)',desc:'(.*?)',url:'(.*?)',tags:\[(.*?)\](?:.*?)\}")
                matches = pattern.findall(content)
                if matches:
                    print(f"[*] Extracted {len(matches)} tools from the artifact.")
                    tools_file = "data/tools.json"
                    existing_tools = {"tools": []}
                    if os.path.exists(tools_file):
                        try:
                            with open(tools_file, "r", encoding="utf-8") as f:
                                existing_tools = json.load(f)
                        except Exception:
                            pass
                    
                    # Prevent duplicates by name
                    existing_names = {t.get("name", "").lower() for t in existing_tools.get("tools", [])}
                    
                    added = 0
                    for m in matches:
                        name = m[1]
                        if name.lower() not in existing_names:
                            existing_tools["tools"].append({
                                "name": name,
                                "category": m[0],
                                "description": m[2].replace("\\'", "'"),
                                "url": m[3]
                            })
                            existing_names.add(name.lower())
                            added += 1
                    
                    if added > 0:
                        with open(tools_file, "w", encoding="utf-8") as f:
                            json.dump(existing_tools, f, indent=2)
                        print(f"[+] Added {added} new tools to data/tools.json")
                    else:
                        print("[*] No new tools found to add.")
                    
                    # Also save the raw text to knowledge base
                    content = f"Imported {len(matches)} OSINT tools from Claude Artifact: {source}"
            elif "text/html" in response.headers.get("Content-Type", ""):
                try:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(content, 'html.parser')
                    content = soup.get_text(separator='\n', strip=True)
                except ImportError:
                    import re
                    content = re.sub(r'<[^>]+>', ' ', content)
        except Exception as e:
            print(f"[-] Failed to fetch from URL: {e}")
            return
    else:
        if os.path.exists(source):
            print(f"[*] Reading material from file: {source}")
            try:
                with open(source, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                print(f"[-] Failed to read file: {e}")
                return
        else:
            print(f"[-] Source is not a valid URL or file path: {source}")
            return
            
    # Save to a knowledge base
    knowledge_dir = "data/knowledge"
    os.makedirs(knowledge_dir, exist_ok=True)
    
    # Generate a simple hash for the filename to avoid duplicates
    source_hash = hashlib.md5(source.encode('utf-8')).hexdigest()[:8]
    filename = f"learned_{source_hash}.txt"
    filepath = os.path.join(knowledge_dir, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"Source: {source}\n")
        f.write("-" * 40 + "\n")
        f.write(content)
        
    print(f"[+] Successfully ingested knowledge from {source}")
    print(f"[+] Saved to {filepath}")
    
    # --- AUTOMATIC OSINT EXTRACTION ---
    import re
    print(f"[*] Extracting OSINT entities from {source}...")
    
    # Extract IPs
    ips = set(re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', content))
    # Extract Emails
    emails = set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', content))
    # Extract Domains (simple approximation)
    domains = set(re.findall(r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b', content))
    
    if ips or emails or domains:
        source_id = db.add_entity("maltego.URL", source)
        
        for ip in ips:
            target_id = db.add_entity("maltego.IPv4Address", ip)
            db.add_relation(source_id, target_id, "Found IP")
            
        for email in emails:
            target_id = db.add_entity("maltego.EmailAddress", email)
            db.add_relation(source_id, target_id, "Found Email")
            
        for domain in domains:
            if "@" not in domain and not any(char.isdigit() for char in domain.split('.')[-1]):
                target_id = db.add_entity("maltego.Domain", domain)
                db.add_relation(source_id, target_id, "Found Domain")
                
        print(f"[+] Extracted {len(ips)} IPs, {len(emails)} Emails, and {len(domains)} Domains!")
        print(f"[*] Entities have been automatically added to the GraphDB!")
    else:
        print("[-] No valid OSINT entities found in the text.")

def chat(args=None):
    # Interactive session for the OSINT agent
    import shlex
    import subprocess
    import json
    import os
    from core.ai_agent import OSINTAgent
    
    agent = OSINTAgent()
    print("\n" + "=" * 65)
    print("      OSINTNeoAi MASTER INTERACTIVE INTELLIGENCE CLI")
    print("=" * 65)
    if agent.gemini_key:
        print("✨ AI Engine: Google Gemini 3.6 Flash (Active - Full Vibe Coding)")
    else:
        print("🛡️ AI Engine: Local Forensic Intelligence (Type 'set key <KEY>' to enable Gemini)")
    print("-" * 65)
    print("Commands:")
    print("  learn <topic/url>    : Ingest URL, file, or concept into GraphDB.")
    print("  transform <name> <v> : Execute transform on target value.")
    print("  transforms list      : List available transforms.")
    print("  correlate / aegis    : Run Aegis Continuous Threat Correlation Engine.")
    print("  tools search <query> : Search across 980+ cataloged OSINT/Kali tools.")
    print("  scan / clis          : Scan local developer CLIs & Google Cloud SDK tools.")
    print("  /model [name]        : Inspect or switch active AI model (gemini, groq, local).")
    print("  status / report      : View live GraphDB and system metrics.")
    print("  legal / statutes     : Statutory authority matrix & federal legal library.")
    print("  retaliation / relator: Whistleblower protections & retaliation evidence.")
    print("  emergency / victims  : Rapid outreach hub (Reddit, legal clinics, newsrooms).")
    print("  help / ?             : Display this command menu.")
    print("  exit / quit          : Exit interactive session.")
    print("-" * 65)
    
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tools_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "tools.json")

    while True:
        try:
            user_input = input("OSINT> ").strip()
            if not user_input:
                user_input = "[USER HIT ENTER]"
            
            if user_input.lower() in ['exit', 'quit']:
                print("[*] Exiting OSINTNeoAi session.")
                break

            # Direct Shell Command Passthrough (if user pastes bash/shell commands into OSINT>)
            if user_input.startswith(('cd ', 'git ', 'ls ', 'pwd', 'curl ', 'npm ', 'cat ', 'grep ', 'rm ', 'mkdir ', 'pip ')) or '&&' in user_input:
                print(f"[*] Executing shell command: {user_input}")
                try:
                    subprocess.run(user_input, shell=True, cwd=root_dir)
                except Exception as e:
                    print(f"[-] Shell execution error: {e}")
                continue

            cmd = user_input.lower()

            if cmd.startswith(('set key ', 'key ', 'api key ', 'set gemini ')):
                new_key = user_input.split(' ', 2)[-1].strip().strip('"').strip("'")
                if len(new_key) > 5:
                    agent.gemini_key = new_key
                    os.environ["GEMINI_API_KEY"] = new_key
                    env_file = os.path.join(root_dir, ".env")
                    with open(env_file, "w", encoding="utf-8") as f:
                        f.write(f"GEMINI_API_KEY={new_key}\n")
                    print(f"[+] Successfully saved GEMINI_API_KEY to {env_file}")
                    print("✨ Google Gemini 3.6 Flash engine is now ACTIVE!")
                else:
                    print("[-] Please provide a valid Gemini API key (e.g. set key AIzaSy...)")
                continue

            if cmd in ['/model', '/models', 'model', 'models']:
                print(agent.list_models_status())
                continue

            elif cmd.startswith(('/model ', 'model ')):
                m_target = user_input.split(' ', 1)[1].strip()
                print(agent.set_model(m_target))
                continue

            elif cmd in ['scan', 'clis', '/scan', 'gcloud scan', 'scan clis', 'scan gcloud', 'tools scan']:
                print("\n" + "=" * 70)
                print("      DEVELOPER CLIS & GOOGLE CLOUD SDK SYSTEM SCANNER")
                print("=" * 70)
                clis = [
                    {"name": "Google Cloud CLI (gcloud)", "cmd": "gcloud"},
                    {"name": "Google BigQuery (bq)", "cmd": "bq"},
                    {"name": "Google Storage (gsutil)", "cmd": "gsutil"},
                    {"name": "GitHub CLI (gh)", "cmd": "gh"},
                    {"name": "Git", "cmd": "git"},
                    {"name": "Azure CLI (az)", "cmd": "az"},
                    {"name": "Docker", "cmd": "docker"},
                    {"name": "Docker Compose", "cmd": "docker-compose"},
                    {"name": "Kubernetes (kubectl)", "cmd": "kubectl"},
                    {"name": "Terraform", "cmd": "terraform"},
                    {"name": "Python", "cmd": "python3" if shutil.which("python3") else "python"},
                    {"name": "Node.js", "cmd": "node"},
                    {"name": "NPM", "cmd": "npm"},
                    {"name": "Antigravity CLI (agy)", "cmd": "agy"},
                    {"name": "cURL", "cmd": "curl"},
                    {"name": "WSL", "cmd": "wsl"}
                ]
                for item in clis:
                    p = shutil.which(item["cmd"])
                    if p:
                        print(f"  🟢 [IN PATH]  {item['name']:<28} : {p}")
                    else:
                        print(f"  ⚪ [MISSING]  {item['name']:<28} : Not in PATH")
                
                print("-" * 70)
                print("  📦 Python Cloud & OSINT Libraries:")
                py_libs = ["google.cloud.bigquery", "google.cloud.storage", "google.cloud.firestore", "g4f", "shodan", "maltego_trx"]
                for lib in py_libs:
                    try:
                        __import__(lib)
                        print(f"  🟢 [INSTALLED] {lib:<28} : Ready")
                    except ImportError:
                        print(f"  ⚪ [NOT FOUND] {lib:<28} : Missing")
                print("=" * 70 + "\n")
                continue
            
            if cmd in ['help', '?']:
                print("\n[*] Available Commands:")
                print("  learn <url/file>     : Scrape and ingest target into GraphDB.")
                print("  transform <name> <v> : Execute a transform on a target.")
                print("  transforms list      : List all Maltego & custom transforms.")
                print("  correlate / aegis    : Execute Aegis BigQuery & Graph Threat Engine.")
                print("  tools search <query> : Search 980+ OSINT & Kali tools.")
                print("  tools list [cat]     : List tools by category.")
                print("  ingest bookmarks     : Re-run mass Chrome bookmarks parser.")
                print("  ingest edr / rico    : Re-run EDR parcel & RICO Shell LLC correlation.")
                print("  ingest kali          : Ingest full Kali Linux security suite.")
                print("  status / report      : Display graph and knowledge statistics.")
                print("  investigate <t> <v>  : Start targeted investigation on an entity.")
                print("  del <id>             : Delete a graph node.")
                print("  exit / quit          : Exit CLI.\n")
                continue
                
            elif cmd in ['status', 'info']:
                db.load()
                nodes = db.data.get("nodes", [])
                edges = db.data.get("edges", []) if len(db.data.get("edges", [])) >= len(db.data.get("links", [])) else db.data.get("links", [])
                t_count = 0
                if os.path.exists(tools_path):
                    with open(tools_path, "r", encoding="utf-8") as f:
                        t_count = len(json.load(f).get("tools", []))
                k_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "knowledge")
                k_count = len(os.listdir(k_dir)) if os.path.exists(k_dir) else 0
                print("\n--- OSINTNeoAi System Status ---")
                print(f"  • Persistent Graph Nodes : {len(nodes):,}")
                print(f"  • Interconnected Edges   : {len(edges):,}")
                print(f"  • Available Tools Matrix : {t_count:,} OSINT/Kali tools")
                print(f"  • Knowledge Digests      : {k_count:,} files in data/knowledge")
                print("--------------------------------\n")
                continue
                
            elif cmd in ['update', 'git pull', 'upgrade']:
                print("[*] Pulling latest updates from GitHub origin/main...")
                subprocess.run(["git", "pull", "origin", "main"], cwd=root_dir)
                print("[+] Updated successfully. Please type 'exit' and re-run 'osintneoai chat' to reload.")
                continue

            elif any(phrase in cmd for phrase in ['correlate', 'aegis', 'threats', 'use all tools', 'map suspects', 'find new connections', 'run all tools']):
                print("[*] Launching Aegis Continuous Threat Correlation & GIS Mapping Engine...")
                aegis_script = os.path.join(root_dir, "aegis_correlation_engine.py")
                if os.path.exists(aegis_script):
                    subprocess.run([os.sys.executable, aegis_script, "--once"])
                else:
                    print(f"[-] aegis_correlation_engine.py not found at {aegis_script}")
                continue
                
            elif cmd in ['ingest bookmarks', 'bookmarks']:
                print("[*] Launching Mass Bookmarks Ingestion Engine...")
                bm_script = os.path.join(root_dir, "ingest_all_bookmarks.py")
                if os.path.exists(bm_script):
                    subprocess.run([os.sys.executable, bm_script])
                else:
                    print(f"[-] ingest_all_bookmarks.py not found at {bm_script}")
                continue
                
            elif cmd in ['ingest edr', 'ingest rico', 'edr', 'rico']:
                print("[*] Launching EDR & RICO Shell LLC Vault Correlation...")
                rico_script = os.path.join(root_dir, "analyze_rico_edr_vault.py")
                if os.path.exists(rico_script):
                    subprocess.run([os.sys.executable, rico_script])
                else:
                    print(f"[-] analyze_rico_edr_vault.py not found at {rico_script}")
                continue
                
            elif cmd in ['ingest kali', 'kali']:
                print("[*] Launching Kali Linux Tool Suite Ingest Engine...")
                kali_script = os.path.join(root_dir, "ingest_kali_linux_suite.py")
                if os.path.exists(kali_script):
                    subprocess.run([os.sys.executable, kali_script])
                else:
                    print(f"[-] ingest_kali_linux_suite.py not found at {kali_script}")
                continue
                
            elif cmd in ['grants', 'nonprofit', 'orr', 'fed grant']:
                print("[*] Launching Federal Grant & Non-Profit Pipeline Analysis...")
                grant_script = os.path.join(root_dir, "trace_orr_grants.py")
                if os.path.exists(grant_script):
                    subprocess.run([os.sys.executable, grant_script])
                else:
                    print(f"[-] trace_orr_grants.py not found at {grant_script}")
                continue

            elif cmd in ['azure', 'azure runner']:
                print("[*] Launching Azure AI Multi-Service Runner...")
                azure_script = os.path.join(root_dir, "azure_runner.py")
                if os.path.exists(azure_script):
                    subprocess.run([os.sys.executable, azure_script])
                else:
                    print(f"[-] azure_runner.py not found at {azure_script}")
                continue

            elif cmd in ['psa', 'social', 'broadcast']:
                print("\n" + "=" * 60)
                print("      OSINT PSA & MULTI-PLATFORM SOCIAL BROADCAST ENGINE")
                print("=" * 60)
                print("  • Public Service Announcement Server : osint_psa_server.py (Port 8080)")
                print("  • Reddit Social Recon                : osint_api_integrations.py")
                print("  • Instagram & Profile Carving        : instaloader / osint_workbook_engine.py")
                print("  • Facebook Graph & Roster Lookup     : osint_api_integrations.py")
                print("  • Federal Evidence Bulletin          : EVIDENCE_FBI_EPA_PSA_HBNC_PLC_COMPROMISE.md")
                print("=" * 60 + "\n")
                continue

            elif cmd in ['legal', 'cite', 'cites', 'statutes', 'referrals']:
                print("\n" + "=" * 65)
                print("      STATUTORY AUTHORITY & LEGAL CITATION REPOSITORY")
                print("=" * 65)
                print("  ⚖️ Federal Criminal RICO     : 18 U.S.C. §§ 1961–1968 (Mail/Wire Fraud & Money Laundering)")
                print("  ⚖️ False Claims Act (CFCA)   : 31 U.S.C. § 3729 et seq. / Cal. Gov. Code § 12650")
                print("  ⚖️ Environmental Crimes      : RCRA 42 U.S.C. § 6901 / CERCLA 42 U.S.C. § 9601")
                print("  ⚖️ Federal Housing Fraud     : 24 C.F.R. Part 570 & Part 58 (HUD Environmental Review)")
                print("  ⚖️ SBA / PPP Loan Fraud      : 15 U.S.C. § 645 (False Statements to SBA)")
                print("  ⚖️ Financial Crimes (FinCEN) : Bank Secrecy Act / 31 U.S.C. § 5318(g)")
                print("  ⚖️ Civil Rights Violations   : 42 U.S.C. § 1983 (Jesse Knabb v. City of HB)")
                print("-" * 65)
                leg_dir = os.path.join(root_dir, "legal_library")
                if os.path.exists(leg_dir):
                    leg_files = os.listdir(leg_dir)
                    print(f"[*] Dossiers in legal_library/ ({len(leg_files)} files):")
                    for lf in leg_files:
                        print(f"  • {lf}")
                print("=" * 65 + "\n")
                continue

            elif cmd in ['retaliation', 'whistleblower', 'relator', 'qui tam']:
                print("\n" + "=" * 70)
                print("   WHISTLEBLOWER & FEDERAL RELATOR RETALIATION EVIDENCE VAULT")
                print("=" * 70)
                print("  🛡️ Federal Relator Protection   : 31 U.S.C. § 3730(h) (False Claims Act Anti-Retaliation)")
                print("  🛡️ State Whistleblower Protection: Cal. Gov. Code § 12653 / Cal. Labor Code § 1102.5")
                print("  🛡️ Criminal Witness Retaliation : 18 U.S.C. § 1513(e) / 18 U.S.C. § 1512 (Witness Tampering)")
                print("  🛡️ Civil Rights Deprivation     : 42 U.S.C. § 1983 / 18 U.S.C. § 241 & § 242 (Color of Law)")
                print("-" * 70)
                print("  [DOCUMENTED RETALIATORY CHRONOLOGY]:")
                print("  1. Jan-Feb 2021: Relator intercedes for Dr. Ann Verma; files formal OCSD IA report.")
                print("  2. Apr-Aug 2021: Shea Properties & OCSD coordinate illegal surprise lockout (212 Southbrook).")
                print("  3. Aug 2021-Pres: Continuous obstruction, storage unit interference, and evidentiary tampering.")
                print("-" * 70)
                print("  [PRIMARY RETALIATION DOSSIERS]:")
                print("  • legal_library/qui_tam_rico_referral_draft.md")
                print("  • legal_library/CFCA_Qui_Tam_Complaint_Draft.md")
                print("  • legal_library/qui_tam_email_inventory.md")
                print("  • legal_library/CRIMINAL_REFERRAL_FINAL.md")
                print("=" * 70 + "\n")
                continue

            elif cmd in ['emergency', 'victim', 'victims', 'outreach', 'activists', 'reddit', 'board', 'victims board']:
                print("\n" + "=" * 75)
                print("   🚨 EMERGENCY VICTIMS, RELATORS & ACTIVIST RAPID OUTREACH HUB")
                print("=" * 75)
                print("  🌐 LIVE OPEN VICTIMS MUTUAL AID BOARD (NO LOGIN REQUIRED):")
                print("  👉 Live Web URL: http://127.0.0.1:5052/victims-board")
                print("     (Accessible on phones, tablets, and PCs to submit, read, or export testimony)")
                print("-" * 75)
                print("  📢 ACTIVE REDDIT DISCUSSION COMMUNITIES (POST YOUR WITNESS STORY/QUESTIONS):")
                print("  • r/orangecounty         : https://www.reddit.com/r/orangecounty/ (Local OC discussions)")
                print("  • r/huntingtonbeach      : https://www.reddit.com/r/huntingtonbeach/ (HB municipal issues)")
                print("  • r/whistleblowers       : https://www.reddit.com/r/whistleblowers/ (Support & advice)")
                print("  • r/legaladvice          : https://www.reddit.com/r/legaladvice/ (Emergency process help)")
                print("  • r/almosthomeless       : https://www.reddit.com/r/almosthomeless/ (Eviction prevention)")
                print("  • r/homeless             : https://www.reddit.com/r/homeless/ (Shelter & survival aid)")
                print("  • r/Journalism           : https://www.reddit.com/r/Journalism/ (Pitching to reporters)")
                print("-" * 75)
                print("  ⚖️ PRO BONO LEGAL DEFENSE & WHISTLEBLOWER INTAKE:")
                print("  • National Whistleblower Center  : https://www.whistleblowers.org/find-an-attorney/")
                print("  • Government Accountability Proj : https://whistleblower.org/get-help/")
                print("  • Community Legal Aid SoCal      : (800) 834-5001 | https://www.communitylegalsocal.org/")
                print("  • Public Law Center (OC)         : (714) 541-1010 | https://www.publiclawcenter.org/")
                print("  • ACLU Southern California       : https://www.aclusocal.org/en/get-legal-help")
                print("-" * 75)
                print("  📰 INVESTIGATIVE NEWSROOM TIP LINES:")
                print("  • Voice of OC (Non-Profit Desk)  : https://voiceofoc.org/contact/")
                print("  • LA Times Investigations Desk   : https://www.latimes.com/tips/")
                print("  • ProPublica Secure Drop         : https://www.propublica.org/tips/")
                print("-" * 75)
                print("  🆘 24/7 CRISIS & RELIEF: Dial 211 or visit https://211oc.org")
                print("  📄 Full Guide: legal_library/EMERGENCY_VICTIMS_ACTIVIST_OUTREACH_HUB.md")
                print("  📄 Local Web App: victims_board.html")
                print("=" * 75 + "\n")
                continue
                
            elif cmd.startswith(('tools search ', 'search ', 'find ', 'tools find ')):
                query = re.sub(r'^(?:tools\s+)?(?:search|find)\s+', '', user_input, flags=re.IGNORECASE).strip().lower()
                if os.path.exists(tools_path):
                    with open(tools_path, "r", encoding="utf-8") as f:
                        t_data = json.load(f).get("tools", [])
                    matches = [t for t in t_data if query in t.get("name", "").lower() or query in t.get("description", "").lower() or query in t.get("category", "").lower()]
                    print(f"\n[*] Found {len(matches)} matching tools for '{query}':")
                    for m in matches[:25]:
                        print(f"  • [{m.get('category')}] {m.get('name')}: {m.get('url')}")
                        if m.get('description'):
                            print(f"    ↳ {m.get('description')}")
                    if len(matches) > 25:
                        print(f"  ... and {len(matches) - 25} more tools.")
                    print("")
                continue
                
            elif cmd.startswith('tools list'):
                parts = cmd.split(' ', 2)
                cat_filter = parts[2].lower() if len(parts) > 2 else None
                if os.path.exists(tools_path):
                    with open(tools_path, "r", encoding="utf-8") as f:
                        t_data = json.load(f).get("tools", [])
                    cats = {}
                    for t in t_data:
                        cats.setdefault(t.get("category", "General"), []).append(t)
                    if cat_filter:
                        matched_cats = {k: v for k, v in cats.items() if cat_filter in k.lower()}
                        print(f"\n[*] Tools matching category '{cat_filter}':")
                        for c_name, t_list in matched_cats.items():
                            print(f"  [{c_name}] ({len(t_list)} tools):")
                            for t in t_list[:15]:
                                print(f"    - {t.get('name')}: {t.get('url')}")
                    else:
                        print(f"\n[*] Tool Categories in Catalog ({len(t_data)} total tools):")
                        for c_name, t_list in cats.items():
                            print(f"  • {c_name}: {len(t_list)} tools")
                        print("\nUse 'tools list <category>' to inspect tools in a specific category.\n")
                continue

            elif cmd.startswith('del '):
                entity_id = cmd.split(' ', 1)[1].strip()
                if db.delete_entity(entity_id):
                    print(f"[*] Deleted entity {entity_id}")
                else:
                    print(f"[-] Entity {entity_id} not found.")
                    
            elif cmd == 'transforms list':
                transforms = trx.list_transforms()
                print("[*] Available Maltego Transforms:")
                for t in transforms:
                    print(f"  - {t}")
                    
            elif cmd.startswith('transform '):
                # Use original user_input to preserve casing for the class name
                parts = user_input.split(' ', 2)
                if len(parts) < 3:
                    print("[-] Usage: transform <TransformName> <TargetValue>")
                    continue
                
                transform_name = parts[1]
                target_value = parts[2]
                
                print(f"[*] Executing {transform_name} on {target_value}...")
                results, error = trx.execute_transform(transform_name, target_value)
                
                if error:
                    print(f"[-] {error}")
                elif results:
                    print(f"[+] Transform returned {len(results)} entities:")
                    source_id = db.add_entity("maltego.Phrase", target_value)
                    for res in results:
                        print(f"  -> [{res['type']}] {res['value']}")
                        target_id = db.add_entity(res['type'], res['value'])
                        db.add_relation(source_id, target_id, transform_name)
                    print(f"[*] Updated GraphDB with new entities.")
                else:
                    print("[-] No entities found.")
                    
            elif cmd.startswith("learn "):
                topic_or_src = user_input[6:].strip()
                if topic_or_src.startswith("http://") or topic_or_src.startswith("https://") or os.path.exists(topic_or_src):
                    class DummyArgs:
                        source = topic_or_src
                    learn(DummyArgs())
                else:
                    print(f"[*] Learning and synthesizing concept: '{topic_or_src}'...")
                    node_id = db.add_entity("maltego.Phrase", topic_or_src)
                    ai_resp = agent.generate_response(f"Explain, define, and synthesize key investigative and coding knowledge for: {topic_or_src}")
                    print(f"\n{ai_resp}\n")
                    db.save()
                    print(f"[+] Ingested '{topic_or_src}' concept into GraphDB (Node ID: {node_id[:8]}...).")
            elif cmd.startswith("investigate "):
                parts = shlex.split(user_input)
                class DummyArgs:
                    type = parts[1]
                    value = parts[2]
                investigate(DummyArgs())
            elif cmd == "report":
                report(None)
            else:
                print("OSINTNeoAi: Thinking...")
                # We need to pass the list of transforms to the AI so it knows what it can execute
                available_transforms = trx.list_transforms()
                trx_str = ", ".join(available_transforms)
                enhanced_input = f"{user_input}\n[Available Transforms: {trx_str}]"
                
                response = agent.generate_response(enhanced_input, investigation_graph)
                
                # Check for agentic execution blocks
                import re
                execute_match = re.search(r'<EXECUTE>(.*?)</EXECUTE>', response)
                
                if execute_match:
                    cmd_str = execute_match.group(1).strip()
                    print(f"[*] AI decided to execute tool: {cmd_str}")
                    
                    parts = cmd_str.split(' ', 1)
                    if len(parts) == 2:
                        transform_name = parts[0]
                        target_value = parts[1]
                        
                        results, error = trx.execute_transform(transform_name, target_value)
                        
                        if error:
                            print(f"[-] Tool failed: {error}")
                            print("OSINTNeoAi: Summarizing error...")
                            final_resp = agent.send_system_message(f"Tool {transform_name} failed: {error}")
                            print(f"\n{final_resp}\n")
                        elif results:
                            source_id = db.add_entity("maltego.Phrase", target_value)
                            for res in results:
                                target_id = db.add_entity(res['type'], res['value'])
                                db.add_relation(source_id, target_id, transform_name)
                            print(f"[+] Tool extracted {len(results)} entities into GraphDB.")
                            print("OSINTNeoAi: Analyzing results...")
                            
                            # Feed results back to AI for summary
                            res_str = "\n".join([f"- {r['type']}: {r['value']}" for r in results])
                            final_resp = agent.send_system_message(f"Tool {transform_name} succeeded. Entities found:\n{res_str}")
                            print(f"\n{final_resp}\n")
                        else:
                            print(f"[-] Tool returned no results.")
                            final_resp = agent.send_system_message(f"Tool {transform_name} returned no results.")
                            print(f"\n{final_resp}\n")
                    else:
                        print("[-] AI provided malformed tool execution syntax.")
                        print(f"\n{response}\n")
                else:
                    # Normal response
                    print(f"\n{response}\n")
        except (KeyboardInterrupt, EOFError):
            break
        except Exception as e:
            print(f"[-] Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="OSINTNeoAi CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # investigate command
    parser_inv = subparsers.add_parser("investigate", help="Start an investigation on a target")
    parser_inv.add_argument("type", help="Type of target (e.g., domain, email)")
    parser_inv.add_argument("value", help="The target value")
    parser_inv.set_defaults(func=investigate)

    # transform command
    parser_trans = subparsers.add_parser("transform", help="Run a transform on a target")
    parser_trans.add_argument("transform", help="Name of the transform (e.g., DomainToIP)")
    parser_trans.add_argument("target", help="The target value to run the transform against")
    parser_trans.set_defaults(func=run_transform)

    # report command
    parser_rep = subparsers.add_parser("report", help="Generate an intelligence report")
    parser_rep.set_defaults(func=report)

    # learn command
    parser_learn = subparsers.add_parser("learn", help="Learn from a file or hyperlink")
    parser_learn.add_argument("source", help="URL or path to the file to learn from")
    parser_learn.set_defaults(func=learn)

    # chat command
    parser_chat = subparsers.add_parser("chat", help="Start an interactive AI chat")
    parser_chat.set_defaults(func=chat)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    args.func(args)

if __name__ == "__main__":
    main()
