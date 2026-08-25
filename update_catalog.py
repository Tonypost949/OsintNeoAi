import os
import json

base = r'C:\Users\Amd949609\OsintNeoAi-1'
report_files = []
skip_dirs = ['.git', '.venv', 'node_modules', '.gemini', '__pycache__']

for root, dirs, files in os.walk(base):
    if any(sd in root for sd in skip_dirs):
        continue
    for f in files:
        if f.endswith(('.md', '.txt', '.pdf', '.docx')):
            if f.startswith('.'):
                continue
            fp = os.path.join(root, f)
            rel = os.path.relpath(fp, base).replace('\\', '/')
            size = os.path.getsize(fp)
            
            title = f
            subtitle = ''
            if f.endswith(('.md', '.txt')):
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
                'kb': round(size / 1024, 1)
            })

report_files.sort(key=lambda x: x['rel'])

# Write reports_catalog.json
with open(os.path.join(base, 'reports_catalog.json'), 'w', encoding='utf-8') as out:
    json.dump(report_files, out, indent=2)

# Write INVESTIGATION_REPORTS_INDEX.md
valid_prefixes = ('legal_library/', 'reports/', 'docs/', 'evidence/', 'opencode_work/')
valid_roots = ('README.md', 'SYSTEM_MANIFEST.md', 'CONTRIBUTING.md')

inv_reports = [
    r for r in report_files 
    if (r['rel'].startswith(valid_prefixes) or r['rel'] in valid_roots)
    and not r['rel'].startswith(('skills/', 'core/skills/', '.agents/', '.gemini/'))
]

categories = {
    "🏛️ Master RICO & Statutory Pleadings": [],
    "💊 Counterfeit Pills, Forensic Doctors & Psychiatric Silencing": [],
    "☣️ Environmental, Toxic Plumes & GeoTracker Audits": [],
    "💰 Financial, PPP Shells, Real Estate & Procurement Audits": [],
    "👶 Foster Care, CPS & Title IV-E Child Removal Investigations": [],
    "🛰️ OSINT Intelligence Reports & Dispatches": []
}

for r in inv_reports:
    title_lower = (r['title'] + " " + r['file'] + " " + r['sub']).lower()
    if any(k in title_lower for k in ['pill', 'pharma', 'mack', 'resnick', 'kushon', 'verma', 'doctor', 'psychiatric', 'clancy', 'intoxication', 'judge decides', 'hi-tech', 'wheat', 'subpoena', 'whitman']):
        categories["💊 Counterfeit Pills, Forensic Doctors & Psychiatric Silencing"].append(r)
    elif any(k in title_lower for k in ['toxic', 'plume', 'chromium', 'cr-vi', 'ascon', 'hazard', 'sinkhole', 'environmental', 'groundwater', 'geotracker']):
        categories["☣️ Environmental, Toxic Plumes & GeoTracker Audits"].append(r)
    elif any(k in title_lower for k in ['ppp', 'procurement', 'contract', 'mercy house', 'lightbox', 'real estate', 'shell', 'weaver', 'financial', 'asset', 'grant']):
        categories["💰 Financial, PPP Shells, Real Estate & Procurement Audits"].append(r)
    elif any(k in title_lower for k in ['cps', 'foster', 'child', 'removal', 'title iv-e', 'trafficking', 'coc undercount']):
        categories["👶 Foster Care, CPS & Title IV-E Child Removal Investigations"].append(r)
    elif any(k in title_lower for k in ['daily', 'weekly', 'dispatch', 'recon', 'scan', 'manifest', 'infrastructure', 'kinetic', 'audit', 'live link']):
        categories["🛰️ OSINT Intelligence Reports & Dispatches"].append(r)
    else:
        categories["🏛️ Master RICO & Statutory Pleadings"].append(r)

lines = [
    "# OSINTNeoAi — MASTER INVESTIGATION REPORTS & DOSSIERS DIRECTORY",
    f"**Total Verified Investigation Reports:** `{len(inv_reports)}`  ",
    "**Access Mode:** Relator & Law Enforcement Privileged  ",
    "**All documents are hyperlinked directly to local file paths.**",
    "",
    "---",
    ""
]

for cat_name, items in categories.items():
    if not items:
        continue
    lines.append(f"## {cat_name} ({len(items)} Documents)")
    lines.append("")
    lines.append("| Document Name | File Path | Size | Summary / Title |")
    lines.append("|---|---|---|---|")
    for it in sorted(items, key=lambda x: x['file']):
        link = f"[`{it['file']}`](file:///C:/Users/Amd949609/OsintNeoAi-1/{it['rel']})"
        sub = f"<br><sub>*{it['sub']}*</sub>" if it['sub'] else ""
        lines.append(f"| {link} | `{it['rel']}` | `{it['kb']} KB` | **{it['title']}**{sub} |")
    lines.append("")

out_index = os.path.join(base, 'legal_library', 'INVESTIGATION_REPORTS_INDEX.md')
with open(out_index, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print(f"[+] Successfully refreshed {out_index} with {len(inv_reports)} documents.")
