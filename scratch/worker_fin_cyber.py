#!/usr/bin/env python3
"""WORKER: Financial anomalies + Cyber/Network deep scan"""
import os, re, json, csv
from pathlib import Path

ROOT = Path(r"C:\OsintNeoAi")
OUT = ROOT / "scratch" / "swarm_output" / "fin_cyber_findings.json"

FIN_PAT = re.compile(
    r"(PPP loan|SBA|unclaimed property|wire transfer|shell company|LLC|nonprofit|"
    r"501c3|501\(c\)\(3\)|fraud|embezzlement|misappropriation|\$[\d,]+|money order|"
    r"tender|LMIHAF|grant|restitution|kickback|bribery|self-dealing|inurement|"
    r"Starpoint|Covenant House|DIS Wealth|Diversified Investment|"
    r"Andrew Do|Peter Pham|Jared Wheat|Hi-Tech Pharm|HOMI|MHI Real|"
    r"Greenglass|1601 Dove|lease-back|Daneshrad|Conway)", re.IGNORECASE
)

CYBER_PAT = re.compile(
    r"(TCP|port scan|exposed endpoint|credential|breach|dehashed|CJIS|"
    r"login|password hash|vulnerability|CVE|open port|RDP|SMB|RPC|"
    r"ransomware|SIM.swap|deepfake|GUID|session token|Wayback|"
    r"hbpd\.org|192\.5\.222\.153|arcgis|FeatureServer|NUWEYT|SM-092|"
    r"Marcus Thorne|Saldivar|74c56b82|EDRnet|Kroll|FTX)", re.IGNORECASE
)

fin_findings = []
cyber_findings = []
dirs_to_scan = [
    ROOT / "evidence",
    ROOT / "reports",
    ROOT / "briefings",
    ROOT / "data",
    ROOT / "forensic",
    ROOT / "master_osint_sheet",
]

scanned = 0
for d in dirs_to_scan:
    if not d.exists():
        continue
    for ext in ["*.txt", "*.md", "*.json", "*.csv"]:
        for fp in d.rglob(ext):
            try:
                content = fp.read_text(encoding="utf-8-sig", errors="replace")[:200_000]
                scanned += 1

                fm = list(FIN_PAT.finditer(content))
                if fm:
                    hits = []
                    for m in fm[:20]:
                        s = max(0, m.start()-100)
                        e = min(len(content), m.end()+250)
                        hits.append({"kw": m.group(0), "ctx": content[s:e].replace("\n"," ").strip()})
                    fin_findings.append({"file": str(fp.relative_to(ROOT)), "hits": len(fm), "samples": hits})

                cm = list(CYBER_PAT.finditer(content))
                if cm:
                    hits = []
                    for m in cm[:20]:
                        s = max(0, m.start()-100)
                        e = min(len(content), m.end()+250)
                        hits.append({"kw": m.group(0), "ctx": content[s:e].replace("\n"," ").strip()})
                    cyber_findings.append({"file": str(fp.relative_to(ROOT)), "hits": len(cm), "samples": hits})

            except Exception:
                pass

# Load structured CSVs
shell_rows, unclaimed_rows, rico_rows = [], [], []
for fname, store in [("Shell_Companies.csv", shell_rows), ("Unclaimed_Prop.csv", unclaimed_rows), ("RICO_Nodes.csv", rico_rows)]:
    p = ROOT / "master_osint_sheet" / fname
    if p.exists():
        with open(p, encoding="utf-8-sig", errors="replace") as f:
            store.extend(list(csv.DictReader(f)))

OUT.write_text(json.dumps({
    "worker": "financial_cyber",
    "files_scanned": scanned,
    "financial": {
        "files_with_hits": len(fin_findings),
        "shell_companies": shell_rows,
        "unclaimed_property": unclaimed_rows,
        "rico_nodes": rico_rows,
        "findings": sorted(fin_findings, key=lambda x: x["hits"], reverse=True)[:150]
    },
    "cyber": {
        "files_with_hits": len(cyber_findings),
        "findings": sorted(cyber_findings, key=lambda x: x["hits"], reverse=True)[:150]
    }
}, indent=2, default=str, ensure_ascii=False), encoding="utf-8")

print(f"[fin_cyber] Done. Scanned {scanned} files. Fin hits: {len(fin_findings)}, Cyber hits: {len(cyber_findings)}")
