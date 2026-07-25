import os
import re

workspace_dir = r"c:\Users\HP\OneDrive\Documents\AG2OSINTNEOMAXX"

keywords = [
    r"\byuxi\b", r"雨希", r"\btai\b", r"\bdjibouti\b", r"\bguinea\b", r"\bcambodia\b", r"柬埔寨", 
    r"\bcongo\b", r"\bmacedonia\b", r"\btimor\b", r"\beast timor\b", r"\baustralia\b"
]

print("Scanning WORKSPACE only (fast)...")
results = []

for root, dirs, files in os.walk(workspace_dir):
    if "node_modules" in root or ".git" in root or ".venv" in root:
        continue
    for file in files:
        filepath = os.path.join(root, file)
        ext = os.path.splitext(file)[1].lower()
        if ext in ['.txt', '.md', '.json', '.xml', '.html', '.htm', '.js', '.py', '.csv', '.bat', '.ps1']:
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                
                text_lower = text.lower()
                found_kws = []
                for pattern in keywords:
                    if re.search(pattern, text_lower, re.IGNORECASE):
                        found_kws.append(pattern)
                
                if found_kws:
                    results.append((filepath, found_kws))
                    print(f"MATCH: {filepath} contains {found_kws}")
            except Exception as e:
                pass

print(f"\nWorkspace Scan complete. Found {len(results)} matching files.")
