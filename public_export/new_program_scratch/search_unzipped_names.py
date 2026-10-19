import os
import re
import json

# Define Search Roots
UNZIPPED_DIR = r"C:\Users\HP\OneDrive\Documents\new_program_scratch\unzipped_data"
AG2_DIR = r"C:\Users\HP\OneDrive\Documents\AG2OSINTNEOMAXX"
OUTPUT_DIR = r"C:\Users\HP\OneDrive\Documents\new_program_scratch"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "comprehensive_rico_suspect_directory.md")

# Simple patterns to match entities, emails, and phone numbers
EMAIL_PAT = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}')
PHONE_PAT = re.compile(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
CORP_PAT = re.compile(r'\b[A-Z][a-zA-Z0-9\s]+(?:LLC|L\.L\.C\.|Corp|Corporation|Inc|Incorporated|Builders|Construction|Trust|Properties|Real Estate|Partners|Group)\b')

def scan_text_for_intel():
    print("[*] Initializing Deep Forensic Scan for Suspects & Co-Conspirators...")
    
    suspects = {
        "individuals": set(),
        "entities": set(),
        "emails": set(),
        "phones": set(),
        "mentions_map": []
    }
    
    # Pre-populate with known confirmed targets to anchor search context
    confirmed_names = [
        "Tom Conway", "Kristy Conway", "Johnny Bryant", "Bryan Pavalko", 
        "Mladen Buntich", "Mike Buntich", "Mia Bergman", "Natalie McCarty", 
        "Paul Julian", "Daryl Cole", "Lisa Rumbaugh", "Paul Daneshrad", 
        "Clayton Chau", "Tamara Escobedo", "Anthony Martinez", "Mitsuru Yamada",
        "Edwin Cabrera", "Jesse Knabb", "Ann Verma"
    ]
    
    # Recursive directory scanning
    scan_paths = [UNZIPPED_DIR, AG2_DIR]
    
    scanned_count = 0
    for base_path in scan_paths:
        if not os.path.exists(base_path):
            continue
            
        print(f"[*] Scanning path: {base_path}...")
        for root, dirs, files in os.walk(base_path):
            if "node_modules" in dirs:
                dirs.remove("node_modules")
            for file in files:
                if file.endswith((".md", ".txt", ".json", ".jsonl", ".csv")):
                    scanned_count += 1
                    full_path = os.path.join(root, file)
                    
                    try:
                        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                            
                        # Extract Emails
                        for em in EMAIL_PAT.findall(content):
                            suspects["emails"].add(em.lower())
                            
                        # Extract Phones
                        for ph in PHONE_PAT.findall(content):
                            suspects["phones"].add(ph)
                            
                        # Extract Corporate entities
                        for corp in CORP_PAT.findall(content):
                            suspects["entities"].add(corp.strip())
                            
                        # Contextual scanning for names
                        for name in confirmed_names:
                            if name in content:
                                # Find surrounding context (sentence)
                                idx = content.find(name)
                                start = max(0, idx - 150)
                                end = min(len(content), idx + len(name) + 150)
                                context_snippet = content[start:end].replace("\n", " ").strip()
                                suspects["mentions_map"].append({
                                    "name": name,
                                    "file": os.path.basename(file),
                                    "context": f"...{context_snippet}..."
                                })
                    except Exception as e:
                        pass

    print(f"[+] Scan complete. Analyzed {scanned_count} text files.")
    
    # Generate suspect directory report
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("# COMPREHENSIVE RICO SUSPECT DIRECTORY\n")
        out.write("`STATUS: CLASSIFIED INTEL / MASTER RECORD`  \n")
        out.write("`GOAL: UNMASK EVERY CO-CONSPIRATOR`  \n\n")
        
        out.write("## 1. PRIMARY TARGETS (INDIVIDUALS)\n\n")
        out.write("| Suspect Name | Implicated Role & Enterprise Mapping |\n")
        out.write("| :--- | :--- |\n")
        for name in sorted(confirmed_names):
            out.write(f"| **{name}** | Primary actor or closely connected node mapped in forensic files. |\n")
            
        out.write("\n## 2. SHUFFLE CONDUITS (LLC / CORPORATE ENTITIES)\n\n")
        out.write("Below are corporate and trust shells extracted across historical chat backups and spreadsheets:\n\n")
        
        # Sort and write up to 100 corporate entities
        filtered_corps = sorted(list(suspects["entities"]))
        for corp in filtered_corps[:100]:
            if len(corp) > 4:  # Filter out noise
                out.write(f"-   **{corp}**\n")
                
        out.write("\n## 3. CONTACT DIRECTORY (COMMUNICATIONS CORRELATION)\n\n")
        out.write("### Email Nodes Extracted:\n")
        for em in sorted(list(suspects["emails"]))[:50]:
            out.write(f"-   `{em}`\n")
            
        out.write("\n### Phone / SMS Terminal Nodes Extracted:\n")
        for ph in sorted(list(suspects["phones"]))[:50]:
            out.write(f"-   `{ph}`\n")
            
        out.write("\n## 4. CONTEXTUAL MENTION MAP (EVIDENTIARY SAMPLES)\n\n")
        out.write("| Name | File Source | Evidence Context Snippet |\n")
        out.write("| :--- | :--- | :--- |\n")
        for entry in suspects["mentions_map"][:50]:
            out.write(f"| {entry['name']} | {entry['file']} | {entry['context']} |\n")

    print(f"[+] Suspicious entity list and contact directory written to: {OUTPUT_FILE}")

if __name__ == "__main__":
    scan_text_for_intel()
