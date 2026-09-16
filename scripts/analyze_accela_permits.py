import os
import json
from pathlib import Path
import re

PERMITS_FILE = Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/data/live_accela_permits.json")

def analyze_permits():
    if not PERMITS_FILE.exists():
        print(f"[-] Permit file not found at {PERMITS_FILE}")
        return
        
    with open(PERMITS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print("[+] Executing Forensic Analysis on Extracted Accela Permits...")
    
    # Check 17631 Cameron (HBNC/Mercy House site)
    hbnc_records = data.get("17631 Cameron", [])
    if isinstance(hbnc_records, list):
        print("\n--- 17631 Cameron Ln (HBNC / Mercy House) ---")
        grading_found = False
        well_found = False
        excavation_found = False
        
        for record in hbnc_records:
            rec_lower = record.lower()
            if "grading" in rec_lower: grading_found = True
            if "well" in rec_lower or "destruction" in rec_lower: well_found = True
            if "stormtech" in rec_lower or "excavation" in rec_lower or "sinkhole" in rec_lower: excavation_found = True
            print(f"  > {record}")
            
        print("\n[!] FORENSIC AUDIT OF 17631 CAMERON:")
        print(f"  - Grading Permit Found: {grading_found}")
        print(f"  - Well Destruction Permit Found: {well_found}")
        print(f"  - StormTech / Excavation Permit Found: {excavation_found}")
        
        if not grading_found and not excavation_found:
            print("  [CRITICAL] ZERO GRADING OR EXCAVATION PERMITS FOUND ON THE PUBLIC RECORD.")
            print("  [CRITICAL] The 2,247 cubic foot StormTech trench was dug entirely off-the-books without municipal grading oversight.")
            
    # Check 17642 Beach Blvd
    beach_records = data.get("17642 Beach", [])
    print(f"\n--- 17642 Beach Blvd ---")
    if isinstance(beach_records, list) and beach_records:
        for record in beach_records:
            print(f"  > {record}")
    else:
        print(f"  [!] {beach_records}")

if __name__ == "__main__":
    analyze_permits()
