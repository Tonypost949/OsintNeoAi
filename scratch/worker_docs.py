#!/usr/bin/env python3
"""WORKER: Deep scan of PDF text layers, DOCX, and JSON registries"""
import re, json, csv, zipfile, io
from pathlib import Path

ROOT = Path(r"C:\OsintNeoAi")
OUT = ROOT / "scratch" / "swarm_output" / "docs_findings.json"

findings = []
json_registry_data = {}

# 1. Scan all JSON files in data/ and master_osint_sheet/
print("[docs] Scanning JSON files...")
for d in [ROOT / "data", ROOT / "master_osint_sheet", ROOT / "reports", ROOT / "briefings"]:
    if not d.exists():
        continue
    for fp in d.rglob("*.json"):
        try:
            sz = fp.stat().st_size
            if sz > 10_000_000:
                findings.append({"file": str(fp.relative_to(ROOT)), "type": "json_large", "size_mb": round(sz/1e6,2), "skipped": True})
                continue
            content = fp.read_text(encoding="utf-8-sig", errors="replace")
            try:
                data = json.loads(content)
                if isinstance(data, dict):
                    keys = list(data.keys())
                    findings.append({"file": str(fp.relative_to(ROOT)), "type": "json", "top_keys": keys[:20], "preview": content[:500]})
                elif isinstance(data, list):
                    findings.append({"file": str(fp.relative_to(ROOT)), "type": "json_list", "length": len(data), "preview": json.dumps(data[:3], default=str)[:500]})
            except json.JSONDecodeError:
                findings.append({"file": str(fp.relative_to(ROOT)), "type": "json_invalid", "preview": content[:200]})
        except Exception as e:
            findings.append({"file": str(fp.relative_to(ROOT)), "type": "json_error", "error": str(e)})

# 2. Scan DOCX files for text content
print("[docs] Scanning DOCX files...")
for d in [ROOT / "evidence", ROOT / "briefings", ROOT / "data"]:
    if not d.exists():
        continue
    for fp in d.rglob("*.docx"):
        try:
            with zipfile.ZipFile(fp) as z:
                if "word/document.xml" in z.namelist():
                    xml = z.read("word/document.xml").decode("utf-8", errors="replace")
                    text = re.sub(r"<[^>]+>", " ", xml)
                    text = re.sub(r"\s+", " ", text).strip()[:3000]
                    findings.append({"file": str(fp.relative_to(ROOT)), "type": "docx", "text_preview": text})
        except Exception as e:
            findings.append({"file": str(fp.relative_to(ROOT)), "type": "docx_error", "error": str(e)})

# 3. Load master_osint_registry.json summary
reg_path = ROOT / "master_osint_sheet" / "master_osint_registry.json"
if reg_path.exists():
    try:
        with open(reg_path, encoding="utf-8-sig", errors="replace") as f:
            reg = json.load(f)
        json_registry_data = {
            "keys": list(reg.keys()),
            "metadata": reg.get("metadata", {}),
            "tab_manifest": reg.get("tab_manifest", [])[:20],
            "master_entity_count": len(reg.get("master_entities", [])),
            "tabs_count": len(reg.get("tabs", {})),
        }
    except Exception as e:
        json_registry_data = {"error": str(e)}

# 4. Scan data/ CSV files
print("[docs] Scanning data/ CSV files...")
data_csvs = []
data_dir = ROOT / "data"
if data_dir.exists():
    for fp in data_dir.rglob("*.csv"):
        try:
            sz = fp.stat().st_size
            if sz > 5_000_000:
                data_csvs.append({"file": str(fp.relative_to(ROOT)), "size_mb": round(sz/1e6,2), "skipped": True})
                continue
            with open(fp, encoding="utf-8-sig", errors="replace") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                data_csvs.append({
                    "file": str(fp.relative_to(ROOT)),
                    "row_count": len(rows),
                    "columns": list(rows[0].keys()) if rows else [],
                    "sample": rows[:3]
                })
        except Exception as e:
            data_csvs.append({"file": str(fp.relative_to(ROOT)), "error": str(e)})

OUT.write_text(json.dumps({
    "worker": "docs",
    "json_registry_summary": json_registry_data,
    "json_and_docx_findings": findings,
    "data_csv_files": data_csvs
}, indent=2, default=str, ensure_ascii=False), encoding="utf-8")

print(f"[docs] Done. {len(findings)} JSON/DOCX files scanned, {len(data_csvs)} data CSVs processed.")
