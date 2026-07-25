import os
import ast
import json

repo_root = r"c:\Users\HP\OneDrive\Documents\OsintNeoAi"

modules = []

exclude_dirs = {'.git', 'node_modules', 'venv', '.venv', '__pycache__', '.pytest_cache', 'dist'}

for root, dirs, files in os.walk(repo_root):
    # Prune excluded directories
    dirs[:] = [d for d in dirs if d not in exclude_dirs]
    
    for f in files:
        if f.endswith('.py'):
            filepath = os.path.join(root, f)
            rel_path = os.path.relpath(filepath, repo_root)
            
            # Read and parse AST
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as file_obj:
                    content = file_obj.read()
                
                tree = ast.parse(content)
                docstring = ast.get_docstring(tree) or "No description provided."
                
                funcs = []
                classes = []
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_doc = ast.get_docstring(node) or "No description."
                        args = [arg.arg for arg in node.args.args]
                        funcs.append({
                            "name": node.name,
                            "docstring": func_doc,
                            "arguments": args,
                            "line": node.lineno
                        })
                    elif isinstance(node, ast.ClassDef):
                        class_doc = ast.get_docstring(node) or "No description."
                        classes.append({
                            "name": node.name,
                            "docstring": class_doc,
                            "line": node.lineno
                        })
                
                modules.append({
                    "file": rel_path.replace('\\', '/'),
                    "description": docstring,
                    "functions": funcs,
                    "classes": classes,
                    "type": "python"
                })
            except Exception as e:
                modules.append({
                    "file": rel_path.replace('\\', '/'),
                    "description": "Python Script",
                    "functions": [],
                    "classes": [],
                    "type": "python"
                })
        elif f.endswith('.sql'):
            filepath = os.path.join(root, f)
            rel_path = os.path.relpath(filepath, repo_root)
            modules.append({
                "file": rel_path.replace('\\', '/'),
                "description": "BigQuery DDL / SQL Analysis Query",
                "functions": [],
                "classes": [],
                "type": "sql"
            })
        elif f.endswith('.md') and not 'node_modules' in root and not '.gemini' in root:
            filepath = os.path.join(root, f)
            rel_path = os.path.relpath(filepath, repo_root)
            modules.append({
                "file": rel_path.replace('\\', '/'),
                "description": "OSINT Investigation Briefing / Markdown Documentation",
                "functions": [],
                "classes": [],
                "type": "markdown"
            })

# Save to scratch folder and also to root directory as modules_data.json
output_path = os.path.join(repo_root, "modules_data.json")
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(modules, f, indent=2)

print(f"Successfully exported {len(modules)} modules to {output_path}")
