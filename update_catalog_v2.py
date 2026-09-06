import os
import json

base = r'C:\OsintNeoAi'
report_files = []
skip_dirs = {'.git', '.venv', 'node_modules', '.gemini', '__pycache__', '.antigravity', '.artifacts', 'extracted_zips', 'archive', 'azure_deploy', 'azure_unzipped_logs'}

for root, dirs, files in os.walk(base):
    dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith('.')]
    for f in files:
        if f.endswith(('.md', '.txt', '.pdf', '.docx', '.csv', '.json', '.html', '.sol')):
            if f.startswith('.'):
                continue
            fp = os.path.join(root, f)
            rel = os.path.relpath(fp, base).replace('\\', '/')
            try:
                size = os.path.getsize(fp)
            except OSError:
                continue
            
            title = f
            subtitle = ''
            category = 'General Document'
            
            if 'legal_library' in rel or 'briefings' in rel or 'cases' in rel:
                category = 'Legal Dossier & Briefing'
            elif 'knowledge_base' in rel:
                category = 'Knowledge Base & RAG'
            elif 'public' in rel or f.endswith('.html'):
                category = 'Dashboard & Map Viewer'
            elif f.endswith('.sol'):
                category = 'Smart Contract & Token'
            elif f.endswith('.csv') or f.endswith('.json'):
                category = 'Structured Dataset & Evidence'
            
            if f.endswith(('.md', '.txt')) and size < 500000:
                try:
                    with open(fp, 'r', encoding='utf-8', errors='ignore') as fh:
                        for line in fh:
                            line = line.strip()
                            if line.startswith('# ') and title == f:
                                title = line.replace('# ', '').strip()
                            elif line.startswith('## ') and not subtitle:
                                subtitle = line.replace('## ', '').strip()
                except Exception:
                    pass
            
            report_files.append({
                'rel': rel,
                'abs': fp.replace('\\', '/'),
                'file': f,
                'title': title,
                'sub': subtitle,
                'category': category,
                'kb': round(size / 1024, 1)
            })

report_files.sort(key=lambda x: (x['category'], x['rel']))

catalog_path = os.path.join(base, 'reports_catalog.json')
with open(catalog_path, 'w', encoding='utf-8') as out:
    json.dump(report_files, out, indent=2)

print(f"[+] Successfully cataloged {len(report_files)} massive library files into {catalog_path}")
