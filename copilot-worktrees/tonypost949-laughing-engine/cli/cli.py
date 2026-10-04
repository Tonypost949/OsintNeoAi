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
    if not investigation_graph:
        print("No entities found. The graph is empty.")
    else:
        print(f"Total entities: {len(investigation_graph)}")
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
        try:
            response = requests.get(source)
            response.raise_for_status()
            content = response.text
            
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
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(content, 'html.parser')
                content = soup.get_text(separator='\n', strip=True)
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
    from core.ai_agent import OSINTAgent
    
    agent = OSINTAgent()
    print("Starting OSINTNeoAiCLI chat session...")
    print("Type 'exit' or 'quit' to end. Commands:")
    print("  learn <url>          : Scrape a URL for entities.")
    print("  transform <name> <v> : Execute a real Maltego transform on a value.")
    print("  transforms list      : List available Maltego transforms.")
    print("  del <id>             : Delete a specific node.")
    while True:
        try:
            user_input = input("OSINT> ").strip()
            if not user_input:
                user_input = "[USER HIT ENTER]"
            
            if user_input.lower() in ['exit', 'quit']:
                break
            
            cmd = user_input.lower()
            if cmd.startswith('del '):
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
                parts = shlex.split(user_input)
                class DummyArgs:
                    source = parts[1]
                learn(DummyArgs())
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
