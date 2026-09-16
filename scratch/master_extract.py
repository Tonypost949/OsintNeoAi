#!/usr/bin/env python3
"""
Master Forensic Extraction Engine
Reads all key CSVs, JSONs, and TXTs from the OsintNeoAi repo.
Outputs a structured findings dict for dossier compilation.
Strict mode: only reports what it finds in files — no inference.
"""
import os, json, csv, re, sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(r"C:\OsintNeoAi")
OSINT_DIR = ROOT / "master_osint_sheet"
EVIDENCE_DIR = ROOT / "evidence"
DATA_DIR = ROOT / "data"
BRIEFINGS_DIR = ROOT / "briefings"
REPORTS_DIR = ROOT / "reports"

findings = {
    "people": [],
    "entities": [],
    "legal_violations": [],
    "financial_anomalies": [],
    "environmental": [],
    "cyber_network": [],
    "timeline_events": [],
    "rico_nodes": [],
    "smoking_guns": [],
    "cross_references": [],
    "evidence_items": [],
    "raw_text_hits": defaultdict(list),
}

LEGAL_KEYWORDS = re.compile(
    r"(perjury|18\s*U\.S\.C|42\s*U\.S\.C|RICO|extortion|wire fraud|mail fraud|"
    r"money laundering|civil rights|due process|UD-101|unlawful detainer|"
    r"default judgment|void judgment|foreclosure|statute|U\.S\.C\.|Cal\.|CCP|Gov\. Code)",
    re.IGNORECASE
)
ENV_KEYWORDS = re.compile(
    r"(hexavalent|chromium|Cr\(VI\)|EPA|CERCLA|RCRA|GeoTracker|toxic|contamination|"
    r"hazardous|groundwater|plume|MCL|ppb|ppm|remediation)",
    re.IGNORECASE
)
CYBER_KEYWORDS = re.compile(
    r"(TCP|port|exposed|credential|breach|hash|dehashed|CJIS|login|password|"
    r"vulnerability|CVE|endpoint|API key|token|firewall|RDP|SMB|RPC|open port)",
    re.IGNORECASE
)
FINANCIAL_KEYWORDS = re.compile(
    r"(PPP loan|SBA|unclaimed property|wire transfer|shell company|LLC|nonprofit|"
    r"501c3|fraud|embezzlement|misappropriation|\$[\d,]+|money order|tender)",
    re.IGNORECASE
)


def read_csv_safe(filepath):
    """Read CSV file, try multiple encodings."""
    for enc in ["utf-8-sig", "latin-1", "cp1252"]:
        try:
            with open(filepath, encoding=enc, errors="replace") as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception:
            continue
    return []


def read_text_safe(filepath, max_bytes=500_000):
    """Read text file with size limit."""
    for enc in ["utf-8-sig", "latin-1", "cp1252"]:
        try:
            with open(filepath, encoding=enc, errors="replace") as f:
                return f.read(max_bytes)
        except Exception:
            continue
    return ""


# ─── 1. MASTER OSINT SHEET CSVs ───────────────────────────────────────────────
print("[*] Processing master_osint_sheet CSVs...")

# People
rows = read_csv_safe(OSINT_DIR / "People.csv")
for r in rows:
    findings["people"].append(dict(r))
print(f"    People: {len(rows)} records")

# RICO Nodes
rows = read_csv_safe(OSINT_DIR / "RICO_Nodes.csv")
for r in rows:
    findings["rico_nodes"].append(dict(r))
print(f"    RICO Nodes: {len(rows)} records")

# Legal Exposure
rows = read_csv_safe(OSINT_DIR / "Legal_Exposure.csv")
for r in rows:
    findings["legal_violations"].append(dict(r))
print(f"    Legal Exposure: {len(rows)} records")

# Smoking Gun Matrix
rows = read_csv_safe(OSINT_DIR / "Smoking_Gun_Matrix.csv")
for r in rows:
    findings["smoking_guns"].append(dict(r))
print(f"    Smoking Gun Matrix: {len(rows)} records")

# Evidence Items
rows = read_csv_safe(OSINT_DIR / "Evidence_Items.csv")
for r in rows:
    findings["evidence_items"].append(dict(r))
print(f"    Evidence Items: {len(rows)} records")

# Timeline
rows = read_csv_safe(OSINT_DIR / "Timeline.csv")
for r in rows:
    findings["timeline_events"].append(dict(r))
print(f"    Timeline: {len(rows)} records")

# Cross References (largest CSV)
rows = read_csv_safe(OSINT_DIR / "Cross_References.csv")
for r in rows:
    findings["cross_references"].append(dict(r))
print(f"    Cross References: {len(rows)} records")

# Toxic Site / Environmental
rows = read_csv_safe(OSINT_DIR / "Toxic_Site.csv")
for r in rows:
    findings["environmental"].append(dict(r))
print(f"    Toxic Site: {len(rows)} records")

# Shell Companies / Financial
rows = read_csv_safe(OSINT_DIR / "Shell_Companies.csv")
for r in rows:
    findings["financial_anomalies"].append({"type": "shell_company", **dict(r)})

rows = read_csv_safe(OSINT_DIR / "Unclaimed_Prop.csv")
for r in rows:
    findings["financial_anomalies"].append({"type": "unclaimed_property", **dict(r)})

rows = read_csv_safe(OSINT_DIR / "CLEANUP_SUMMARY.csv")
for r in rows:
    findings["financial_anomalies"].append({"type": "cleanup_summary", **dict(r)})

# MASTER.csv
rows = read_csv_safe(OSINT_DIR / "MASTER.csv")
print(f"    MASTER.csv: {len(rows)} records")
for r in rows:
    findings["entities"].append(dict(r))

# SPARK Correlations (most recent)
rows = read_csv_safe(OSINT_DIR / "SPARK_Correlations.csv")
print(f"    SPARK Correlations: {len(rows)} records")
for r in rows:
    findings["cross_references"].append({"source": "SPARK", **dict(r)})

# ─── 2. MASTER REGISTRY JSON ──────────────────────────────────────────────────
print("[*] Processing master_osint_registry.json...")
try:
    with open(OSINT_DIR / "master_osint_registry.json", encoding="utf-8-sig", errors="replace") as f:
        registry = json.load(f)
    print(f"    Registry keys: {list(registry.keys())[:10]}")
    # Store summary
    findings["raw_text_hits"]["registry_summary"].append(
        f"Top-level keys: {list(registry.keys())}"
    )
    # Extract sub-entities if they exist
    for key in ["people", "entities", "cases", "properties", "violations"]:
        if key in registry and isinstance(registry[key], list):
            print(f"    Registry[{key}]: {len(registry[key])} items")
            findings["raw_text_hits"][f"registry_{key}"] = registry[key][:100]
except Exception as e:
    print(f"    [!] Registry JSON error: {e}")

# ─── 3. EVIDENCE TEXT FILES (keyword scan) ────────────────────────────────────
print("[*] Scanning evidence .txt files (keyword extraction)...")
txt_files = list(EVIDENCE_DIR.rglob("*.txt"))
print(f"    Found {len(txt_files)} .txt files")

hit_count = 0
for fp in txt_files[:800]:  # cap at 800 for speed
    content = read_text_safe(fp, max_bytes=50_000)
    if not content:
        continue
    rel = str(fp.relative_to(ROOT))
    
    if LEGAL_KEYWORDS.search(content):
        # Extract surrounding context of hits
        for m in LEGAL_KEYWORDS.finditer(content):
            start = max(0, m.start() - 100)
            end = min(len(content), m.end() + 200)
            snippet = content[start:end].replace("\n", " ").strip()
            findings["raw_text_hits"]["legal"].append({"file": rel, "snippet": snippet})
            hit_count += 1
            if hit_count > 2000:
                break
    
    if ENV_KEYWORDS.search(content):
        for m in ENV_KEYWORDS.finditer(content):
            start = max(0, m.start() - 100)
            end = min(len(content), m.end() + 200)
            snippet = content[start:end].replace("\n", " ").strip()
            findings["raw_text_hits"]["environmental"].append({"file": rel, "snippet": snippet})
    
    if CYBER_KEYWORDS.search(content):
        for m in CYBER_KEYWORDS.finditer(content):
            start = max(0, m.start() - 100)
            end = min(len(content), m.end() + 200)
            snippet = content[start:end].replace("\n", " ").strip()
            findings["raw_text_hits"]["cyber"].append({"file": rel, "snippet": snippet})
    
    if FINANCIAL_KEYWORDS.search(content):
        for m in FINANCIAL_KEYWORDS.finditer(content):
            start = max(0, m.start() - 100)
            end = min(len(content), m.end() + 200)
            snippet = content[start:end].replace("\n", " ").strip()
            findings["raw_text_hits"]["financial"].append({"file": rel, "snippet": snippet})

print(f"    Legal hits: {len(findings['raw_text_hits']['legal'])}")
print(f"    Env hits:   {len(findings['raw_text_hits']['environmental'])}")
print(f"    Cyber hits: {len(findings['raw_text_hits']['cyber'])}")
print(f"    Fin hits:   {len(findings['raw_text_hits']['financial'])}")

# ─── 4. EVIDENCE .md FILES ────────────────────────────────────────────────────
print("[*] Scanning evidence .md files...")
md_files = list(EVIDENCE_DIR.rglob("*.md"))
for fp in md_files:
    content = read_text_safe(fp)
    rel = str(fp.relative_to(ROOT))
    findings["raw_text_hits"]["md_files"].append({"file": rel, "content": content[:3000]})
print(f"    Found {len(md_files)} .md files")

# ─── 5. BRIEFINGS ─────────────────────────────────────────────────────────────
print("[*] Scanning briefings directory...")
for ext in ["*.md", "*.txt", "*.json"]:
    for fp in BRIEFINGS_DIR.rglob(ext):
        content = read_text_safe(fp)
        rel = str(fp.relative_to(ROOT))
        findings["raw_text_hits"]["briefings"].append({"file": rel, "content": content[:5000]})
print(f"    Briefing files scanned: {len(findings['raw_text_hits']['briefings'])}")

# ─── 6. DATA DIR JSON/CSV ─────────────────────────────────────────────────────
print("[*] Scanning data directory...")
data_hits = []
for ext in ["*.json", "*.csv"]:
    for fp in DATA_DIR.rglob(ext):
        try:
            sz = fp.stat().st_size
            if sz > 5_000_000:  # skip >5MB
                data_hits.append({"file": str(fp.relative_to(ROOT)), "size_mb": round(sz/1e6,2), "skipped": True})
                continue
            content = read_text_safe(fp, max_bytes=100_000)
            data_hits.append({"file": str(fp.relative_to(ROOT)), "preview": content[:2000]})
        except Exception as e:
            data_hits.append({"file": str(fp.relative_to(ROOT)), "error": str(e)})
findings["raw_text_hits"]["data_dir"] = data_hits
print(f"    Data files scanned: {len(data_hits)}")

# ─── 7. REPORTS DIR ───────────────────────────────────────────────────────────
print("[*] Scanning reports directory...")
report_hits = []
for ext in ["*.md", "*.txt", "*.json", "*.csv"]:
    for fp in REPORTS_DIR.rglob(ext):
        content = read_text_safe(fp, max_bytes=30_000)
        report_hits.append({"file": str(fp.relative_to(ROOT)), "content": content[:5000]})
findings["raw_text_hits"]["reports"] = report_hits
print(f"    Report files scanned: {len(report_hits)}")

# ─── 8. SAVE FULL EXTRACTION ──────────────────────────────────────────────────
print("[*] Saving extraction results...")
out_path = ROOT / "scratch" / "extraction_results.json"
out_path.parent.mkdir(exist_ok=True)

# Convert defaultdict for JSON serialization
findings["raw_text_hits"] = dict(findings["raw_text_hits"])

with open(out_path, "w", encoding="utf-8") as f:
    json.dump(findings, f, indent=2, default=str, ensure_ascii=False)

print(f"[✓] Extraction complete → {out_path}")
print(f"[✓] Summary:")
for k, v in findings.items():
    if k != "raw_text_hits":
        print(f"    {k}: {len(v)} records")
    else:
        for subk, subv in v.items():
            print(f"    raw_text_hits.{subk}: {len(subv)} items")
