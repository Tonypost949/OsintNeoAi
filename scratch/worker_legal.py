#!/usr/bin/env python3
"""WORKER: Legal & Statutory violations deep scan"""
import os, re, json, csv
from pathlib import Path

ROOT = Path(r"C:\OsintNeoAi")
OUT = ROOT / "scratch" / "swarm_output" / "legal_findings.json"

PATTERNS = re.compile(
    r"(perjury|18\s*U\.S\.C|42\s*U\.S\.C|RICO|extortion|wire fraud|mail fraud|"
    r"money laundering|civil rights|due process|UD-101|unlawful detainer|"
    r"default judgment|void judgment|CCP\s*§|Gov\.\s*Code|Cal\.\s*Civ|"
    r"whistleblower|relator|qui tam|false claims|restitution|indictment|"
    r"convicted|sentenced|felony|misdemeanor|statute of limitations|"
    r"Cal\.\s*CCP|U\.S\.C\.\s*§|31\s*U\.S\.C|18\s*U\.S\.C)", re.IGNORECASE
)

findings = []
dirs_to_scan = [
    ROOT / "evidence",
    ROOT / "briefings",
    ROOT / "reports",
    ROOT / "legal_library",
    ROOT / "cases",
    ROOT / "FEDERAL_SUBMISSION",
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
                        s = max(0, m.start()-120)
                        e = min(len(content), m.end()+250)
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
            except Exception as ex:
                pass

# Also parse Legal_Exposure.csv
le_path = ROOT / "master_osint_sheet" / "Legal_Exposure.csv"
legal_rows = []
if le_path.exists():
    with open(le_path, encoding="utf-8-sig", errors="replace") as f:
        legal_rows = list(csv.DictReader(f))

OUT.write_text(json.dumps({
    "worker": "legal",
    "files_scanned": scanned,
    "files_with_hits": len(findings),
    "legal_exposure_records": legal_rows,
    "findings": sorted(findings, key=lambda x: x["hit_count"], reverse=True)[:200]
}, indent=2, default=str, ensure_ascii=False), encoding="utf-8")

print(f"[legal] Done. Scanned {scanned} files, {len(findings)} with legal hits.")
