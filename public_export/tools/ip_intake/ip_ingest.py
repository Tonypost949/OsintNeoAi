#!/usr/bin/env python3
"""ip_ingest.py - IP Intake & Forensic Sweep (provenance-first)

Scans a directory tree for IPv4/IPv6 addresses in text sources (and PDFs when
pdftotext is available), classifies every address, dedupes per source file, and
emits a full provenance chain: file path, SHA-256, line number, context, and the
UTC extraction stamp.

Outputs (into --out):
  ip_occurrences.jsonl                  one row per (file, ip) first occurrence
  ip_rollup.csv                         one row per unique IP (global)
  source_manifest.csv                   every scanned file + sha256 + size + mtime
  summary.json                          machine-readable totals
  PUBLIC_IPS_FORENSIC_SWEEP_DOSSIER.md  human-readable public-IP dossier

Usage:
  python3 ip_ingest.py --root /path/to/tree --out /path/to/out [--label NAME]
"""

import argparse
import csv
import hashlib
import ipaddress
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

TOOL_VERSION = "1.0.1"

TEXT_EXT = {
    ".txt", ".md", ".markdown", ".json", ".jsonl", ".csv", ".tsv", ".log",
    ".html", ".htm", ".xml", ".yml", ".yaml", ".sql", ".py", ".js", ".mjs",
    ".cjs", ".ts", ".tsx", ".jsx", ".kt", ".kts", ".java", ".cs", ".c", ".h",
    ".cpp", ".hpp", ".go", ".rs", ".rb", ".php", ".sh", ".bash", ".ps1",
    ".bat", ".cmd", ".vue", ".css", ".scss", ".ini", ".cfg", ".conf", ".env",
    ".toml", ".rst", ".rtf", ".eml", ".mbox", ".ipynb", ".srt", ".vtt",
}
PDF_EXT = {".pdf"}
SKIP_DIRS = {
    ".git", ".hg", ".svn", ".venv", "venv", "node_modules", "__pycache__",
    ".cache", ".mypy_cache", ".pytest_cache", "dist", "build",
}

IPV4_RE = re.compile(
    r"(?<![\d.])"
    r"(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)"
    r"(?:\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}"
    r"(?![\d.])"
)
IPV6_CAND_RE = re.compile(
    r"(?<![0-9A-Fa-f:.])(?:[0-9A-Fa-f]{0,4}:){2,7}[0-9A-Fa-f]{0,4}(?![0-9A-Fa-f:.])"
)

CGNAT = ipaddress.ip_network("[IP_REDACTED]/10")


def classify(ip_str):
    try:
        a = ipaddress.ip_address(ip_str)
    except ValueError:
        return None
    if a.is_global:
        return "public"
    if a.is_loopback:
        return "loopback"
    if a.is_link_local:
        return "link_local"
    if a.is_multicast:
        return "multicast"
    if a.is_unspecified:
        return "unspecified"
    if a.version == 4 and a in CGNAT:
        return "shared_cgnat"
    if a.is_private:
        return "private"
    if a.is_reserved:
        return "reserved"
    return "non_global"


def extract_ips(text):
    """Yield (normalized_ip, line_no, context) for every valid IP occurrence."""
    for lineno, line in enumerate(text.splitlines(), 1):
        seen_line = set()
        for m in IPV4_RE.finditer(line):
            ip = classify(m.group(0))
            if ip:
                norm = str(ipaddress.ip_address(m.group(0)))
                if norm in seen_line:
                    continue
                seen_line.add(norm)
                yield norm, lineno, line.strip()[:180]
        for m in IPV6_CAND_RE.finditer(line):
            cand = m.group(0)
            if ":" not in cand:
                continue
            start, end = m.span()
            before = line[start - 1] if start > 0 else ""
            after = line[end] if end < len(line) else ""
            # CSS pseudo-elements (::before/::after) and word fragments produce
            # technically-valid shorthand like "::bef" and "e::" - drop anything
            # glued to letters, plus single ultra-short groups.
            if (before and before.isalpha()) or (after and after.isalpha()):
                continue
            groups = [g for g in cand.split(":") if g]
            if len(groups) == 1 and len(groups[0]) < 3:
                continue
            try:
                addr = ipaddress.ip_address(cand)
            except ValueError:
                continue
            if addr.version != 6:
                continue
            norm = str(addr)
            if norm in seen_line:
                continue
            seen_line.add(norm)
            yield norm, lineno, line.strip()[:180]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sniff_binary(path):
    try:
        with open(path, "rb") as f:
            head = f.read(4096)
    except OSError:
        return True
    return b"\x00" in head


def read_text_file(path, ext):
    if ext in PDF_EXT:
        if not shutil.which("pdftotext"):
            return None, "pdf_no_extractor"
        try:
            r = subprocess.run(
                ["pdftotext", "-layout", str(path), "-"],
                capture_output=True, text=True, timeout=120, errors="ignore",
            )
        except (subprocess.TimeoutExpired, OSError):
            return None, "pdf_error"
        if r.returncode != 0:
            return None, "pdf_error"
        return r.stdout, None
    if sniff_binary(path):
        return None, "binary"
    try:
        raw = Path(path).read_bytes()
    except OSError:
        return None, "read_error"
    for enc in ("utf-8", "utf-16", "latin-1"):
        try:
            return raw.decode(enc), None
        except (UnicodeDecodeError, LookupError):
            continue
    return raw.decode("utf-8", errors="ignore"), None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--label", default=None)
    ap.add_argument("--max-filesize-mb", type=float, default=6.0)
    ap.add_argument("--max-pdf-mb", type=float, default=20.0)
    ap.add_argument("--no-pdf", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    label = args.label or root.name
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    t0 = time.time()

    max_bytes = int(args.max_filesize_mb * 1024 * 1024)
    max_pdf_bytes = int(args.max_pdf_mb * 1024 * 1024)

    occurrences = []          # dicts
    rollup = {}               # ip -> dict
    manifest = []             # dicts
    skipped = Counter()
    files_scanned = 0
    files_text = 0
    files_pdf = 0
    occurrences_total = 0

    def rel(p):
        try:
            return str(p.relative_to(root))
        except ValueError:
            return str(p)

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for fn in sorted(filenames):
            p = Path(dirpath) / fn
            ext = p.suffix.lower()
            try:
                st = p.stat()
            except OSError:
                skipped["stat_error"] += 1
                continue
            if p.is_symlink():
                skipped["symlink"] += 1
                continue
            if ext in PDF_EXT:
                if args.no_pdf:
                    skipped["pdf_disabled"] += 1
                    continue
                cap = max_pdf_bytes
            elif ext in TEXT_EXT:
                cap = max_bytes
            else:
                skipped["ext_filtered"] += 1
                continue
            if st.st_size == 0:
                skipped["empty"] += 1
                continue
            if st.st_size > cap:
                skipped["oversize"] += 1
                continue

            text, why = read_text_file(p, ext)
            if text is None:
                skipped[why or "unreadable"] += 1
                continue
            files_scanned += 1
            if ext in PDF_EXT:
                files_pdf += 1
            else:
                files_text += 1

            digest = sha256_file(p)
            per_file = {}
            for ip, lineno, ctx in extract_ips(text):
                occurrences_total += 1
                if ip in per_file:
                    per_file[ip]["count"] += 1
                    continue
                per_file[ip] = {"count": 1, "line": lineno, "ctx": ctx}
                cls = classify(ip)
                rec = {
                    "ip": ip,
                    "version": ipaddress.ip_address(ip).version,
                    "class": cls,
                    "file": rel(p),
                    "sha256": digest,
                    "line": lineno,
                    "context": ctx,
                    "occurrences_in_file": 1,
                    "extracted_at": stamp,
                }
                occurrences.append(rec)
                r = rollup.setdefault(ip, {
                    "ip": ip, "version": rec["version"], "class": cls,
                    "occurrences": 0, "files": set(),
                    "first_file": rel(p), "first_line": lineno, "first_ctx": ctx,
                })
                r["occurrences"] += 1
                r["files"].add(rel(p))

            manifest.append({
                "file": rel(p), "sha256": digest, "size": st.st_size,
                "mtime_utc": datetime.fromtimestamp(st.st_mtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "type": "pdf" if ext in PDF_EXT else "text",
                "ips_in_file": len(per_file),
            })
            # keep occurrences_in_file in sync
            if per_file:
                for o in occurrences[-len(per_file):]:
                    o["occurrences_in_file"] = per_file[o["ip"]]["count"]

            if files_scanned % 500 == 0:
                print(f"[ip_ingest] scanned {files_scanned} files, "
                      f"{len(rollup)} unique IPs so far...", file=sys.stderr)

    # finalize rollup for CSV
    rows = []
    for ip, r in rollup.items():
        rows.append({
            "ip": ip, "version": r["version"], "class": r["class"],
            "occurrences": r["occurrences"], "files": len(r["files"]),
            "first_file": r["first_file"], "first_line": r["first_line"],
            "first_context": r["first_ctx"],
        })
    rows.sort(key=lambda x: (-x["occurrences"], x["ip"]))

    with open(out / "ip_occurrences.jsonl", "w", encoding="utf-8") as f:
        for o in occurrences:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")

    with open(out / "ip_rollup.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else
                           ["ip", "version", "class", "occurrences", "files",
                            "first_file", "first_line", "first_context"])
        w.writeheader()
        w.writerows(rows)

    with open(out / "source_manifest.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["file", "sha256", "size", "mtime_utc", "type", "ips_in_file"])
        w.writeheader()
        w.writerows(manifest)

    class_counts = Counter(r["class"] for r in rows)
    public_rows = [r for r in rows if r["class"] == "public"]
    public_files = Counter()
    for r in public_rows:
        for o in occurrences:
            if o["ip"] == r["ip"] and o["class"] == "public":
                public_files[o["file"]] += 1

    summary = {
        "tool": f"ip_ingest {TOOL_VERSION}",
        "label": label,
        "root": str(root),
        "generated_at": stamp,
        "duration_sec": round(time.time() - t0, 1),
        "files_scanned": files_scanned,
        "files_text": files_text,
        "files_pdf": files_pdf,
        "files_skipped": dict(skipped),
        "ip_occurrences_total": occurrences_total,
        "unique_ips": len(rows),
        "classes": dict(class_counts),
        "public_ips": len(public_rows),
        "top_public": [
            {"ip": r["ip"], "occurrences": r["occurrences"], "files": r["files"],
             "first": f'{r["first_file"]}:{r["first_line"]}'}
            for r in public_rows[:25]
        ],
    }
    with open(out / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # ---- human-readable dossier ----
    lines = []
    lines.append(f"# Public IP Forensic Sweep Dossier - {label}\n")
    lines.append(f"- **Generated (UTC):** {stamp}")
    lines.append(f"- **Tool:** ip_ingest {TOOL_VERSION} (provenance-first, Law 15)")
    lines.append(f"- **Source root:** `{root}`")
    lines.append(f"- **Files scanned:** {files_scanned} text/PDF "
                 f"({files_text} text, {files_pdf} PDF)")
    lines.append(f"- **IP occurrences:** {occurrences_total}")
    lines.append(f"- **Unique IPs:** {len(rows)} | **Public:** {len(public_rows)}")
    classes_txt = ", ".join(f"{k}={v}" for k, v in sorted(class_counts.items()))
    lines.append(f"- **Classes:** {classes_txt}\n")

    lines.append("## 1. Public IPs (ranked by occurrences)\n")
    lines.append("| # | IP | Occ | Files | First source | Context |")
    lines.append("|---|----|-----|-------|--------------|---------|")
    for i, r in enumerate(public_rows[:500], 1):
        ctx = r["first_context"].replace("|", "\\|")[:90]
        src = f'{r["first_file"]}:{r["first_line"]}'.replace("|", "\\|")
        lines.append(f'| {i} | {r["ip"]} | {r["occurrences"]} | {r["files"]} | `{src}` | {ctx} |')
    if len(public_rows) > 500:
        lines.append(f"\n_(showing top 500 of {len(public_rows)} public IPs; full set in ip_rollup.csv)_")
    lines.append("")

    lines.append("## 2. Source files carrying public IPs\n")
    lines.append("| File | Public IPs |")
    lines.append("|------|------------|")
    for fn, c in public_files.most_common(50):
        lines.append(f'| `{fn}` | {c} |')
    lines.append("")

    lines.append("## 3. Non-public classes\n")
    lines.append("| Class | Unique IPs |")
    lines.append("|-------|------------|")
    for k, v in sorted(class_counts.items()):
        lines.append(f"| {k} | {v} |")
    lines.append("")

    lines.append("## 4. Provenance & method\n")
    lines.append("- Every occurrence stores: source file (relative path), SHA-256 of "
                 "the exact file version, line number, and a context snippet.")
    lines.append("- Deduplication is per (file, IP); the rollup aggregates across files.")
    lines.append("- Classification via Python `ipaddress` (public = globally routable).")
    lines.append("- PDFs are extracted with `pdftotext -layout` when available; "
                 "scanned/image-only PDFs yield no text and are skipped.")
    lines.append("- Extraction is deterministic: same tree + same tool version => "
                 "same outputs. Re-run to refresh after new files land.")
    lines.append("")
    (out / "PUBLIC_IPS_FORENSIC_SWEEP_DOSSIER.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"[ip_ingest] done in {summary['duration_sec']}s | files={files_scanned} "
          f"| occurrences={occurrences_total} | unique={len(rows)} | public={len(public_rows)}")
    print(f"[ip_ingest] outputs -> {out}")


if __name__ == "__main__":
    main()
