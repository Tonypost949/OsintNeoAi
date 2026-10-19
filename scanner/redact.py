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
    "large_data", "backup-scripts", "chat_logs",
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
# A phone number must carry at least one separator or parenthesis. A bare
# ten-digit run is ambiguous: in the source corpus it is overwhelmingly a
# court case number, file number, or timestamp, and matching it destroyed
# official identifiers such as "26SMUD01464".
PHONE_RE = re.compile(
    r"(?<!\d)(?:\+?1[\s.-]?)?(?:\(\d{3}\)\s?|\d{3}[\s.-])\d{3}[\s.-]\d{4}(?!\d)"
)
EMAIL_RE = re.compile(r"\b([A-Za-z0-9._%+-])[A-Za-z0-9._%+-]*@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b")
DOB_RE = re.compile(
    r"\b(0?[1-9]|1[0-2])[/-](0?[1-9]|[12]\d|3[01])[/-]((?:19|20)\d{2})\b"
)
# Street addresses in California records almost always carry a directional
# prefix ("1133 N Formosa Ave", "29757 W*** Rd"). Without the
# optional directional token the address pattern cannot match them at all,
# which let unmasked residential addresses through the gate.
ADDRESS_RE = re.compile(
    r"\b(\d{1,6})\s+(?:([NSEW]{1,2})\.?\s+)?"
    r"([A-Z][A-Za-z0-9.'’-]+(?:\s+[A-Z][A-Za-z0-9.'’-]+){0,3})\s+"
    r"(Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Court|Ct|"
    r"Way|Place|Pl|Terrace|Ter|Circle|Cir|Parkway|Pkwy|Highway|Hwy|Plaza)\b"
)
ZIP_RE = re.compile(r"\b(\d{3})\d{2}(?:-\d{4})?\b")
# Labeled identifiers ("Case No. 26SMUD01464", "Account #12345"). The value
# must be identifier-shaped: uppercase letters, digits and hyphens, and it
# must contain at least one digit. Without that constraint the pattern
# matched ordinary prose that merely follows a trigger word, which silently
# corrupted published text ("case strength" -> "case ****ngth",
# "Case References" -> "Case ****nces").
LABELED_ID_RE = re.compile(
    r"(?i:\b(account|acct|loan|policy|claim|case|driver'?s?[- ]?license|"
    r"dl|passport|member|medicaid|medicare)\s*(?:no\.?|number|#)?\s*[:#]?\s*)"
    r"(?=[A-Z0-9-]*\d)([A-Z0-9][A-Z0-9-]{4,})"
)
# Dates of birth are frequently written in prose form, for example a
# month-name form or a spelled-out date. The numeric-only pattern misses
# those. A year-only value is already the minimum the policy permits, so it
# is deliberately not matched here.
DOB_TEXT_RE = re.compile(
    r"(?i)\b(?:DOB|Date of Birth)\b(?P<sep>\s*[:\-]?\s*)"
    r"(?P<month>[A-Z][a-z]{2,9}\.?\s+(?:\d{1,2},?\s*)?|\d{1,2}[/-]\d{1,2}[/-])"
    r"(?P<year>(?:19|20)\d{2})"
)
# One combined pass for the high-volume identifier patterns. Public-record
# line logic is applied per match so already-public records stay untouched.
COMBINED_RE = re.compile(
    r"(?P<ssn>(?<!\d)(?P<ssn_area>\d{3})[-\s](?P<ssn_mid>\d{2})[-\s](?P<ssn_last>\d{4})(?!\d))"
    r"|(?P<phone>(?<!\d)(?:\+?1[\s.-]?)?(?:\(\d{3}\)\s?|\d{3}[\s.-])(?P<phone_mid>\d{3})[\s.-](?P<phone_last>\d{4})(?!\d))"
    r"|(?P<email>(?P<email_first>[A-Za-z0-9._%+-])[A-Za-z0-9._%+-]*@(?P<email_domain>[A-Za-z0-9.-]+\.[A-Za-z]{2,}))"
    r"|(?P<dob>(?<!\d)(?P<dob_m>0?[1-9]|1[0-2])[/-](?P<dob_d>0?[1-9]|[12]\d|3[01])[/-](?P<dob_y>(?:19|20)\d{2})(?!\d))"
    r"|(?P<address>(?P<addr_num>\d{1,6})\s+(?:(?P<addr_dir>[NSEW]{1,2})\.?\s+)?(?P<addr_name>[A-Z][A-Za-z0-9.'’-]+(?:\s+[A-Z][A-Za-z0-9.'’-]+){0,3})\s+(?P<addr_suffix>Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Court|Ct|Way|Place|Pl|Terrace|Ter|Circle|Cir|Parkway|Pkwy|Highway|Hwy|Plaza)\b)"
    r"|(?P<zip>(?<![A-Za-z0-9-])(?P<zip3>\d{3})\d{2}(?:-\d{4})?(?![A-Za-z0-9-]))"
    r"|(?P<labeled>(?i:\b(?P<label>account|acct|loan|policy|claim|case|driver'?s?[- ]?license|dl|passport|member|medicaid|medicare)\s*(?:no\.?|number|#)?\s*[:#]?\s*)(?=[A-Z0-9-]*\d)(?P<label_value>[A-Z0-9][A-Z0-9-]{4,})(?![A-Za-z0-9@._%+-]))"
)
OFFICIAL_URL_RE = re.compile(r"https?://[^\s]*(?:\.gov|\.us)(?=[/\s?#]|$)", re.I)
OFFICIAL_EMAIL_DOMAIN = re.compile(r"\.(?:gov|mil|us)$", re.I)
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
    # Very long fused/minified lines can trigger pathological regex behavior.
    # Do not publish them unscanned; the file is moved to review instead.
    if len(line) > 50_000:
        counts["long_line_unscanned"] += 1
        return line

    def combined_sub(m: re.Match) -> str:
        gd = m.groupdict()
        if gd.get("ssn") is not None:
            counts["ssn"] += 1
            return "***-**-" + gd["ssn_last"]
        if gd.get("phone") is not None:
            # A phone number is only passed through when the same line also
            # carries an official government URL. Otherwise it is masked.
            if public_line and OFFICIAL_URL_RE.search(line):
                return m.group(0)
            counts["phone"] += 1
            return "(***) ***-" + gd["phone_last"]
        if gd.get("email") is not None:
            # Personal mailbox providers are masked even on public-record
            # lines. Only official government/military mailboxes pass through.
            if public_line and OFFICIAL_EMAIL_DOMAIN.search(gd["email_domain"]):
                return m.group(0)
            counts["email"] += 1
            return gd["email_first"] + "***@" + gd["email_domain"]
        if gd.get("dob") is not None:
            if public_line:
                return m.group(0)
            counts["dob"] += 1
            return "**/**/" + gd["dob_y"]
        if gd.get("address") is not None:
            if public_line:
                return m.group(0)
            counts["address"] += 1
            name = gd["addr_name"]
            # The directional prefix ("N", "SW") is part of the masked form so
            # the record stays locatable within its own jurisdiction.
            direction = (gd["addr_dir"] + ". ") if gd.get("addr_dir") else ""
            return f"{gd['addr_num']} {direction}{name[0]}*** {gd['addr_suffix']}"
        if gd.get("zip") is not None:
            if public_line:
                return m.group(0)
            counts["zip"] += 1
            return gd["zip3"] + "**"
        if gd.get("labeled") is not None:
            label = gd["label"]
            value = re.sub(r"[^A-Za-z0-9]", "", gd["label_value"])
            if label.lower().startswith(("case", "docket", "claim")):
                # A case, docket, or claim number is an official public
                # identifier. It is never a personal account identifier, and
                # masking it destroys the citation value of the record.
                return m.group(0)
            counts["account"] += 1
            return label + " ****" + value[-4:]
        return m.group(0)

    line = COMBINED_RE.sub(combined_sub, line)
    line = SECRET_ASSIGN_RE.sub(
        lambda m: (counts.update(["secret_assignment"]) or
                   m.group(1) + "=[REDACTED]"), line)

    def dob_text_sub(m: re.Match) -> str:
        if public_line:
            return m.group(0)
        counts["dob"] += 1
        label = m.group(0)[:m.start("sep") - m.start(0)]
        return f"{label}{m.group('sep')}**/**/{m.group('year')}"
    line = DOB_TEXT_RE.sub(dob_text_sub, line)

    def ip_sub(m: re.Match) -> str:
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
    return IPV4_RE.sub(ip_sub, line)


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
    size = src.stat().st_size
    if size > 1_000_000:
        rec["status"] = "review_large_file"
        return rec
    with src.open("rb") as f:
        head = f.read(4096)
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
    auth_context_hint = re.compile(
        r"(?i)\b(source|authority|official record|public record|retrieved)\b")
    for line in lines:
        line_public = is_public_line(line)
        # Only an authoritative URL that is explicitly presented as a source or
        # authority opens a short pass-through window. A bare URL is not enough.
        if line_public or (AUTH_URL_RE.search(line) and auth_context_hint.search(line)):
            public_context = 6
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
    needs_review = (counts.get("long_line_unscanned", 0) > 0 or
                    (strict and structured and (not has_url or not has_auth)))
    if needs_review:
        rec["status"] = "review_long_line" if counts.get("long_line_unscanned") else "review_missing_citation"
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
            if name.startswith("chat_export") or name == "chat.html":
                continue
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
