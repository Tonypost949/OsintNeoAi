import os

workspace_root = r"c:\Users\HP\OneDrive\Documents\OsintNeoAi"

subdirs = [
    "OSINTNeoAI-Core",
    "OSINTNeoAiCLI",
    "OSINTNeoAiXL",
    "OsintNeoAi",
    "OsintNeoAi52026",
    "OsintNeoAiXXXL",
    "osint-agent",
    "osint_analyzer",
    "riconow"
]

print("=== OSINT REPOS COUNT SUMMARY ===")
for subdir in subdirs:
    full_path = os.path.join(workspace_root, subdir)
    if os.path.exists(full_path):
        py_count = 0
        js_count = 0
        md_count = 0
        all_dirs = []
        for root, dirs, files in os.walk(full_path):
            for d in dirs:
                rel = os.path.relpath(os.path.join(root, d), full_path)
                if rel.count(os.sep) < 2 and not any(part.startswith('.') or part in ('__pycache__', 'node_modules', 'venv') for part in rel.split(os.sep)):
                    all_dirs.append(rel)
            for f in files:
                if f.endswith('.py'):
                    py_count += 1
                elif f.endswith(('.js', '.ts', '.tsx')):
                    js_count += 1
                elif f.endswith('.md'):
                    md_count += 1
        print(f"\n[DIR] Directory: {subdir}")
        print(f"   Python files: {py_count}")
        print(f"   JS/TS files: {js_count}")
        print(f"   Markdown files: {md_count}")
        print(f"   Key Subfolders: {', '.join(sorted(list(set(all_dirs)))[:10])}")
