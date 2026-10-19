#!/usr/bin/env python3
"""Verify that a public export contains no hard secrets or unapproved identifiers.

Hard failures: secrets, unredacted SSNs, private IPs, full personal email
addresses, and non-official phone numbers. Government/military email domains
and already-masked mailbox local parts are allowed. Phone numbers are allowed
only on an official .gov/.us source line or when the line is clearly a format
example/placeholder.
"""
from __future__ import annotations
import argparse, ipaddress, json, re, sys
from pathlib import Path

TEXT_EXT = {".md",".txt",".html",".htm",".csv",".json",".jsonl",".ndjson",".py",
            ".js",".ts",".tsx",".jsx",".css",".yml",".yaml",".xml",".kml",
            ".sql",".sh",".toml",".ini",".cfg",".rst",".tex"}
HARD = [
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("github_fine_grained", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("stripe_live_key", re.compile(r"\bsk_live_[0-9A-Za-z]{16,}\b")),
]
SSN = re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)")
IPV4 = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE = re.compile(r"(?<!\d)(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}(?!\d)")
OFFICIAL_URL = re.compile(r"https?://[^\s]*(?:\.gov|\.us)(?=[/\s?#]|$)", re.I)
OFFICIAL_EMAIL_DOMAIN = re.compile(r"\.(?:gov|mil|us)$", re.I)
CARRIER_GATEWAY = re.compile(
    r"(?i)@(?:vms\.t-mobile\.com|vtext\.com|txt\.att\.net|"
    r"messaging\.sprintpcs\.com|tmomail\.net)$")
MASKED_PHONE = re.compile(r"\(\*{3}\)\s*\*{3}-\d{3,4}")
PLACEHOLDER = re.compile(
    r"(?i)\b(?:e\.g\.|example|sample|placeholder|format|canonical|normalizer)\b")


def email_allowed(email: str, line: str) -> bool:
    local, _, domain = email.partition("@")
    if "*" in local:
        return True
    if OFFICIAL_EMAIL_DOMAIN.search(domain):
        return True
    # A carrier voicemail gateway is a masked phone number, not a mailbox.
    if CARRIER_GATEWAY.search("@" + domain) and MASKED_PHONE.search(line):
        return True
    return False


def phone_allowed(phone: str, line: str) -> bool:
    if OFFICIAL_URL.search(line):
        return True
    # The public tree contains normalizer format examples such as
    # "###-###-#### (e.g. 178-431-1400)". They are not contact records.
    return bool(PLACEHOLDER.search(line))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", default="VERIFY_REPORT.json")
    a = ap.parse_args()
    root = Path(a.root).resolve()
    findings = []
    counts = {
        "files": 0, "hard_secret": 0, "unredacted_ssn": 0, "private_ip": 0,
        # Backwards-compatible fields: these now mean *unapproved* matches,
        # not "no matches exist". Totals are reported separately.
        "emails": 0, "phones": 0,
        "emails_total": 0, "emails_allowed": 0, "emails_disallowed": 0,
        "phones_total": 0, "phones_allowed": 0, "phones_disallowed": 0,
        "oversize": 0,
    }
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        if p.stat().st_size > 100 * 1024 * 1024:
            counts["oversize"] += 1
            findings.append({"path": rel.as_posix(), "rule": "file_over_100mb"})
            continue
        if p.suffix.lower() not in TEXT_EXT:
            continue
        counts["files"] += 1
        text = p.read_text(encoding="utf-8", errors="replace")
        for name, rx in HARD:
            if rx.search(text):
                counts["hard_secret"] += 1
                findings.append({"path": rel.as_posix(), "rule": name})
        if SSN.search(text):
            counts["unredacted_ssn"] += 1
            findings.append({"path": rel.as_posix(), "rule": "unredacted_ssn"})
        for m in IPV4.finditer(text):
            try:
                ip = ipaddress.ip_address(m.group(0))
            except ValueError:
                continue
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                counts["private_ip"] += 1
                findings.append({"path": rel.as_posix(), "rule": "private_ip"})
                break
        for line in text.splitlines():
            for m in EMAIL.finditer(line):
                counts["emails_total"] += 1
                if email_allowed(m.group(0), line):
                    counts["emails_allowed"] += 1
                else:
                    counts["emails_disallowed"] += 1
                    counts["emails"] += 1
                    findings.append({"path": rel.as_posix(), "rule": "unapproved_email"})
            for m in PHONE.finditer(line):
                counts["phones_total"] += 1
                if phone_allowed(m.group(0), line):
                    counts["phones_allowed"] += 1
                else:
                    counts["phones_disallowed"] += 1
                    counts["phones"] += 1
                    findings.append({"path": rel.as_posix(), "rule": "unapproved_phone"})
    report = {
        # Never publish an absolute VM/local path in this report.
        "root": "public_export",
        "counts": counts,
        "findings": findings[:1000],
        "pass": not findings,
    }
    Path(a.out).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"pass": report["pass"], "counts": counts}, sort_keys=True))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
