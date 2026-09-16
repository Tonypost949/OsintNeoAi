#!/usr/bin/env python3
"""WORKER: Environmental hazards deep scan"""
import os, re, json, csv
from pathlib import Path

ROOT = Path(r"C:\OsintNeoAi")
OUT = ROOT / "scratch" / "swarm_output" / "env_findings.json"

PATTERNS = re.compile(
    r"(hexavalent|chromium|Cr\(VI\)|Cr-VI|EPA|CERCLA|RCRA|DTSC|GeoTracker|"
    r"toxic|contamination|hazardous|groundwater|plume|MCL|ppb|ppm|"
    r"remediation|asphalt cap|well|W-4150|T10000018579|20IC002|"
    r"petroleum|hydrocarbons|TPH|arsenic|lead|benzene|PCE|TCE|"
    r"Phase I|Phase II|ESA|environmental site|OCHCA|RWQCB|"
    r"Cameron Ln|Beach Blvd|17631|17642|Ascon|superfund|"
    r"Water Code|Porter-Cologne|Title 27|CEQA)", re.IGNORECASE
)

findings = []
dirs_to_scan = [
    ROOT / "evidence",
    ROOT / "reports",
    ROOT / "briefings",
    ROOT / "data",
    ROOT / "forensic",
]

scanned = 0
for d in dirs_to_scan:
    if not d.exists():
        continue
    for ext in ["*.txt", "*.md", "*.json", "*.csv"]:
        for fp in d.rglob(ext):
            try:
                content = fp.read_text(encoding="utf-8-sig", errors="replace")[:200_000]
                matches = list(PATTERNS.finditer(content))
                if matches:
                    hits = []
                    for m in matches[:30]:
                        s = max(0, m.start()-100)
                        e = min(len(content), m.end()+300)
                        hits.append({
                            "keyword": m.group(0),
                            "context": content[s:e].replace("\n", " ").strip()
                        })
                    findings.append({
                        "file": str(fp.relative_to(ROOT)),
                        "hit_count": len(matches),
                        "hits": hits
                    })
                scanned += 1
            except Exception:
                pass

# Parse Toxic_Site CSV
toxic_rows = []
tp = ROOT / "master_osint_sheet" / "Toxic_Site.csv"
if tp.exists():
    with open(tp, encoding="utf-8-sig", errors="replace") as f:
        toxic_rows = list(csv.DictReader(f))

OUT.write_text(json.dumps({
    "worker": "environmental",
    "files_scanned": scanned,
    "files_with_hits": len(findings),
    "toxic_site_records": toxic_rows,
    "findings": sorted(findings, key=lambda x: x["hit_count"], reverse=True)[:200]
}, indent=2, default=str, ensure_ascii=False), encoding="utf-8")

print(f"[env] Done. Scanned {scanned} files, {len(findings)} with env hits.")
