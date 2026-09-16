#!/usr/bin/env python3
"""WORKER: Timeline reconstruction + entity cross-reference"""
import re, json, csv
from pathlib import Path

ROOT = Path(r"C:\OsintNeoAi")
OUT = ROOT / "scratch" / "swarm_output" / "timeline_findings.json"

DATE_PAT = re.compile(
    r"(\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
    r"\s+\d{1,2},?\s+20\d{2}\b|\b20\d{2}-\d{2}-\d{2}\b|\b\d{1,2}/\d{1,2}/20\d{2}\b)",
    re.IGNORECASE
)

timeline_hits = []
dirs_to_scan = [
    ROOT / "evidence",
    ROOT / "briefings",
    ROOT / "reports",
    ROOT / "master_osint_sheet",
    ROOT / "timeline_calendar",
]

scanned = 0
for d in dirs_to_scan:
    if not d.exists():
        continue
    for ext in ["*.txt", "*.md", "*.csv"]:
        for fp in d.rglob(ext):
            try:
                content = fp.read_text(encoding="utf-8-sig", errors="replace")[:150_000]
                dates = DATE_PAT.findall(content)
                if len(dates) >= 3:
                    timeline_hits.append({
                        "file": str(fp.relative_to(ROOT)),
                        "date_count": len(dates),
                        "dates_found": list(set(dates))[:30],
                        "preview": content[:1000].replace("\n"," ").strip()
                    })
                scanned += 1
            except Exception:
                pass

# Load structured timeline CSVs
timeline_rows = []
for fname in ["Timeline.csv", "MASTER_TIMELINE.csv", "TIMELINE_CHART_2020_2026.csv", "Wintersburg_Timeline.csv"]:
    p = ROOT / "master_osint_sheet" / fname
    if p.exists():
        with open(p, encoding="utf-8-sig", errors="replace") as f:
            rows = list(csv.DictReader(f))
            timeline_rows.append({"file": fname, "rows": rows})

OUT.write_text(json.dumps({
    "worker": "timeline",
    "files_scanned": scanned,
    "files_with_dates": len(timeline_hits),
    "structured_timelines": timeline_rows,
    "document_timeline_hits": sorted(timeline_hits, key=lambda x: x["date_count"], reverse=True)[:100]
}, indent=2, default=str, ensure_ascii=False), encoding="utf-8")

print(f"[timeline] Done. Scanned {scanned} files, {len(timeline_hits)} with timeline data.")
