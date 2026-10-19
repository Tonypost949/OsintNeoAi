#!/usr/bin/env python3
"""Fail-closed public-export redactor and citation auditor.

Local/private input is never modified. The scanner writes a redacted copy to
`public_export/`, holds uncited structured records in `review_queue/`, and
refuses to publish files containing hard secrets or unsupported binaries.

Usage:
  python3 scanner/redact.py --source /path/to/private --out /path/to/public \
      --strict-citations
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import ipaddress
import json
import os
import re
import shutil
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ALLOWED_EXT = {
    ".md", ".txt", ".html", ".htm", ".csv", ".json", ".jsonl", ".ndjson",
    ".py", ".js", ".ts", ".tsx", ".jsx", ".css", ".yml", ".yaml", ".xml",
    ".kml", ".sql", ".sh", ".toml", ".ini", ".cfg", ".rst", ".tex",
}
SKIP_DIRS = {
    ".git", "node_modules", ".next", "venv", ".venv", "env", "__pycache__",
    "quarantine", "review_queue", "public_export", ".cache", "dist", "build",
    "backups", "backup", "cloud_storage", "Amd949609_keys", "repos",
    "evidence", "data", "agent", "extracted_documents", "sessions",
    "scratch", "opencode_work", "extracted_home_data", "exports",
    "large_data", "backup-scripts",
}
SENSITIVE_NAME = re.compile(
    r"(fullz|pii|personal|identity|ssn|social[-_]?security|credit[-_]?card|"
    r"medical|patient|bank|routing|tax|passport|driver|dl_|victim|minor|"
    r"credential|secret|token|cookie|session|private[-_]?key)",
    re.I,
)

# Hard secrets: the whole file is quarantined.
HARD_SECRETS = [
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("github_fine_grained", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("private_key", re.compile(
        r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"
        r"[\s\S]{20,}?-----END (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"
    )),
    ("bearer_token", re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{25,}\b")),
]

# Soft secrets: redact the value but keep the document.
SOFT_SECRETS = [
    ("password_assignment", re.compile(
        r"(?i)\b(password|passwd|pwd)\s*[:=]\s*['\"]?([^\s'\"<>]{6,})"
    )),
    ("secret_assignment", re.compile(
        r"(?i)\b(secret|api[_-]?key|access[_-]?token|auth[_-]?token)\s*[:=]\s*"
        r"['\"]?([^\s'\"<>]{8,})"
    )),
]

SSN_RE = re.compile(r"(?<!\d)(\d{3})[-\s](\d{2})[-\s](\d{4})(?!\d)")
PHONE_RE = re.compile(
    r"(?<!\d)(?:\+?1[\s.-]?)?\(?([2-9]\d{2})\)?[\s.-]?(\d{3})[\s.-]?(\d{4})(?!\d)"
)
EMAIL_RE = re.compile(r"\b([A-Za-z0-9._%+-])[A-Za-z0-9._%+-]*@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b")
DOB_RE = re.compile(
    r"\b(0?[1-9]|1[0-2])[/-](0?[1-9]|[12]\d|3[01])[/-]((?:19|20)\d{2})\b"
)
ADDRESS_RE = re.compile(
    r"\b(\d{1,6})\s+([A-Z][A-Za-z0-9.'-]+(?:\s+[A-Z][A-Za-z0-9.'-]+){0,3})\s+"
    r"(Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Court|Ct|"
    r"Way|Place|Pl|Terrace|Ter|Circle|Cir|Parkway|Pkwy|Highway|Hwy)\b"
)
ZIP_RE = re.compile(r"\b(\d{3})\d{2}(?:-\d{4})?\b")
LABELED_ID_RE = re.compile(
    r"(?i)\b(account|acct|loan|policy|claim|case|driver'?s?[- ]?license|"
    r"dl|passport|member|medicaid|medicare)\s*(?:no\.?|number|#)?\s*[:#]?\s*"
    r"([A-Z0-9-]{5,})"
)
IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
SECRET_ASSIGN_RE = re.compile(
    r"(?i)\b(password|passwd|pwd|secret|api[_-]?key|access[_-]?token|"
    r"auth[_-]?token|cookie)\s*[:=]\s*['\"]?([^\s'\"<>]{6,})"
)
URL_RE = re.compile(r"https?://[^\s<>\)\]\"']+", re.I)
AUTH_URL_RE = re.compile(
    r"https?://[^\s<>\)\]\"']*(?:\.gov|\.us|\.court|\.state\.[a-z]{2}\.us|"
    r"clerk|recorder|assessor|supreme|uscourts|courtlistener|legislature|"
    r"justice|sheriff|county|city)[^\s<>\)\]\"']*",
    re.I,
)
AUTHORITY_RE = re.compile(
    r"(?i)\b(superior court|district court|court of appeal|supreme court|"
    r"county|city of|state of|department|agency|office|clerk|recorder|"
    r"assessor|sheriff|statute|code|§|u\.s\.c\.|cal\.|case no|docket|"
    r"official record|public record)\b"
)
LEGAL_RE = re.compile(
    r"(?i)(§|\bu\.s\.c\.|\bcal\.|\bcode\b|\bstatute\b|\bsec\.|\bsection\b|"
    r"\bcase no\b|\bcitation\b|\blegal\b)"
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def is_public_line(line: str) -> bool:
    if not URL_RE.search(line):
        return False
    return bool(AUTH_URL_RE.search(line) or
                (AUTHORITY_RE.search(line) and re.search(r"(?i)public record|official record", line)))


def redact_line(line: str, counts: Counter, public_line: bool) -> str:
    # Hard/soft secrets first.
    for name, rx in HARD_SECRETS:
        if rx.search(line):
            counts[name] += 1
    for name, rx in SOFT_SECRETS:
        def soft_sub(m):
            counts[name] += 1
            return m.group(1) + "=[REDACTED]"
        line = rx.sub(soft_sub, line)
    line = SECRET_ASSIGN_RE.sub(lambda m: (counts.update(["secret_assignment"]) or
                                           m.group(1) + "=[REDACTED]"), line)

    # High-risk identifiers are always masked, even on public-record lines.
    def ssn_sub(m):
        counts["ssn"] += 1
        return "***-**-" + m.group(3)
    line = SSN_RE.sub(ssn_sub, line)

    def account_sub(m):
        label, value = m.group(1), re.sub(r"[^A-Za-z0-9]", "", m.group(2))
        # Public case/docket numbers are citations, not financial identifiers.
        if public_line and label.lower().startswith(("case", "docket", "claim")):
            return m.group(0)
        counts["account"] += 1
        return label + " ****" + value[-4:]
    line = LABELED_ID_RE.sub(account_sub, line)

    if not public_line:
        def phone_sub(m):
            counts["phone"] += 1
            return "(***) ***-" + m.group(3)
        line = PHONE_RE.sub(phone_sub, line)

        def email_sub(m):
            counts["email"] += 1
            return m.group(1) + "***@" + m.group(2)
        line = EMAIL_RE.sub(email_sub, line)

        def dob_sub(m):
            counts["dob"] += 1
            return "**/**/" + m.group(3)
        line = DOB_RE.sub(dob_sub, line)

        def addr_sub(m):
            counts["address"] += 1
            name = m.group(2)
            return f"{m.group(1)} {name[0]}*** {m.group(3)}"
        line = ADDRESS_RE.sub(addr_sub, line)

        def zip_sub(m):
            counts["zip"] += 1
            return m.group(1) + "**"
        line = ZIP_RE.sub(zip_sub, line)

    # IP policy: private/reserved always masked; public only when cited.
    def ip_sub(m):
        raw = m.group(0)
        try:
            ip = ipaddress.ip_address(raw)
        except ValueError:
            return raw
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            counts["private_ip"] += 1
            return "[PRIVATE_IP]"
        if public_line:
            return raw
        counts["public_ip_masked"] += 1
        return "[IP_REDACTED]"
    line = IPV4_RE.sub(ip_sub, line)
    return line


def process_file(src: Path, rel: Path, out_root: Path, review_root: Path,
                 strict: bool) -> dict:
    rec = {
        "path": rel.as_posix(),
        "sha256": sha256(src),
        "bytes": src.stat().st_size,
        "status": "published",
        "rules": {},
        "citation": {},
    }
    if src.stat().st_size > 8 * 1024 * 1024:
        rec["status"] = "skipped_large"
        return rec
    head = src.read_bytes()[:4096]
    if b"\x00" in head:
        rec["status"] = "skipped_binary"
        return rec
    try:
        text = src.read_text(encoding="utf-8", errors="replace")
    except Exception:
        rec["status"] = "skipped_unreadable"
        return rec

    hard_hit = [name for name, rx in HARD_SECRETS if rx.search(text)]
    if hard_hit:
        rec["status"] = "quarantined_secret"
        rec["rules"] = {"hard_secret": len(hard_hit)}
        # Do not copy the file anywhere public.
        return rec

    counts: Counter = Counter()
    lines = text.splitlines(keepends=True)
    redacted_lines = []
    public_context = 0
    for line in lines:
        line_public = is_public_line(line)
        if line_public or (URL_RE.search(line) and
                           (AUTHORITY_RE.search(line) or
                            re.search(r"(?i)\b(source|official|public record|retrieved)\b", line))):
            public_context = 12
        effective_public = line_public or public_context > 0
        redacted_lines.append(redact_line(line, counts, effective_public))
        if public_context > 0:
            public_context -= 1
    redacted = "".join(redacted_lines)

    has_url = bool(URL_RE.search(text))
    has_auth = bool(AUTHORITY_RE.search(text))
    has_legal = bool(LEGAL_RE.search(text))
    rec["citation"] = {
        "source_url": has_url,
        "authority": has_auth,
        "legal_section": has_legal,
    }
    rec["rules"] = dict(counts)

    # Structured records with no source/authority are held, not published.
    structured = rel.suffix.lower() in {".json", ".jsonl", ".ndjson", ".csv"}
    needs_review = strict and structured and (not has_url or not has_auth)
    if needs_review:
        rec["status"] = "review_missing_citation"
        dest = review_root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(redacted, encoding="utf-8")
        return rec

    dest = out_root / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(redacted, encoding="utf-8")
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--strict-citations", action="store_true")
    ap.add_argument("--clean", action="store_true")
    args = ap.parse_args()

    source = Path(args.source).resolve()
    out = Path(args.out).resolve()
    public = out / "public_export"
    review = out / "review_queue"
    if args.clean:
        for p in (public, review):
            if p.exists():
                shutil.rmtree(p)
    public.mkdir(parents=True, exist_ok=True)
    review.mkdir(parents=True, exist_ok=True)

    records = []
    for root, dirs, files in os.walk(source):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS
                   and not d.startswith(".git")
                   and not d.startswith("evidence＂ --include")]
        for name in files:
            src = Path(root) / name
            rel = src.relative_to(source)
            if SENSITIVE_NAME.search(rel.as_posix()):
                records.append({"path": rel.as_posix(), "status": "quarantined_sensitive_name",
                                "sha256": sha256(src), "bytes": src.stat().st_size,
                                "rules": {}, "citation": {}})
                continue
            if src.suffix.lower() not in ALLOWED_EXT:
                continue
            if any(part in SKIP_DIRS for part in rel.parts):
                continue
            try:
                records.append(process_file(src, rel, public, review, args.strict_citations))
            except Exception as e:
                records.append({"path": rel.as_posix(), "status": "error",
                                "error": type(e).__name__, "rules": {}, "citation": {}})

    counts = Counter(r["status"] for r in records)
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": str(source),
        "strict_citations": args.strict_citations,
        "files_total": len(records),
        "status_counts": dict(counts),
        "records": records,
    }
    (out / "PUBLIC_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"files_total": len(records), "status_counts": dict(counts)},
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
