"""
Searches downloads files for disgrace/national and outputs everything to disgrace_matches.txt.
"""
import os
import json

def main():
    dl_dir = r"C:\Users\HP\Downloads"
    terms = ["disgrace", "national"]
    out = []
    
    # Also check the project files
    proj_dir = r"c:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent"
    
    dirs = [dl_dir, proj_dir]
    
    for d in dirs:
        if not os.path.exists(d):
            continue
        out.append(f"\n========================================\nSCANNING DIRECTORY: {d}\n========================================\n")
        
        for root, _, files in os.walk(d):
            # Skip virtualenv and git folders
            if "venv" in root or ".git" in root or "__pycache__" in root:
                continue
            for f in files:
                if f.endswith(".json") or f.endswith(".txt") or f.endswith(".md"):
                    path = os.path.join(root, f)
                    try:
                        with open(path, 'r', encoding='utf-8', errors='ignore') as file:
                            content = file.read()
                        
                        found = [t for t in terms if t.lower() in content.lower()]
                        if found:
                            out.append(f"\nMatch in file: {os.path.relpath(path, d)} (Terms: {found})\n")
                            lines = content.split('\n')
                            for i, l in enumerate(lines):
                                if any(t.lower() in l.lower() for t in terms):
                                    start = max(0, i-2)
                                    end = min(len(lines), i+3)
                                    out.append(f"  --- Line {i+1} ---\n")
                                    for j in range(start, end):
                                        prefix = "  >>> " if j == i else "      "
                                        out.append(f"{prefix}{lines[j]}\n")
                    except Exception as e:
                        pass
                        
    with open("disgrace_matches.txt", "w", encoding="utf-8") as f:
        f.write("".join(out))

if __name__ == "__main__":
    main()
