import os

workspace_dir = r"C:\Users\HP\OneDrive\Documents\AG2OSINTNEOMAXX"
brain_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d"

keywords = ["SOS", "Secretary of State", "registered agent", "agent name", "agent_name", "agent_string"]

def scan_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        if any(x in root for x in [".git", ".venv", "__pycache__", "node_modules", "deepseek_data"]):
            continue
        for file in files:
            if file.endswith((".md", ".txt", ".csv")):
                filepath = os.path.join(root, file)
                if os.path.getsize(filepath) > 1024 * 1024: # skip files > 1MB
                    continue
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        for kw in keywords:
                            if kw.lower() in content.lower():
                                print(f"MATCH: {os.path.relpath(filepath, folder_path)} (keyword: {kw})")
                                lines = content.split("\n")
                                for i, line in enumerate(lines):
                                    if kw.lower() in line.lower() and len(line.strip()) < 300:
                                        print(f"  L{i+1}: {line.strip()[:150]}")
                                break
                except Exception as e:
                    pass

print("=== SCANNING WORKSPACE ===")
scan_folder(workspace_dir)
print("\n=== SCANNING BRAIN ===")
scan_folder(brain_dir)
