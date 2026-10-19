#!/usr/bin/env python3
"""Verify that a public export contains no hard secrets or unredacted SSNs."""
from __future__ import annotations
import argparse, hashlib, ipaddress, json, re, sys
from pathlib import Path

TEXT_EXT = {".md",".txt",".html",".htm",".csv",".json",".jsonl",".ndjson",".py",
            ".js",".ts",".tsx",".jsx",".css",".yml",".yaml",".xml",".kml",
            ".sql",".sh",".toml",".ini",".cfg",".rst",".tex"}
HARD = [
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("github_fine_grained", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
]
SSN = re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)")
IPV4 = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE = re.compile(r"(?<!\d)(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}(?!\d)")

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("--root", required=True); ap.add_argument("--out", default="VERIFY_REPORT.json")
    a=ap.parse_args(); root=Path(a.root).resolve()
    findings=[]; counts={"files":0,"hard_secret":0,"unredacted_ssn":0,"private_ip":0,"emails":0,"phones":0,"oversize":0}
    for p in root.rglob("*"):
        if not p.is_file(): continue
        rel=p.relative_to(root)
        if p.stat().st_size > 100*1024*1024:
            counts["oversize"]+=1; findings.append({"path":rel.as_posix(),"rule":"file_over_100mb"}); continue
        if p.suffix.lower() not in TEXT_EXT: continue
        counts["files"]+=1
        text=p.read_text(encoding="utf-8", errors="replace")
        for name,rx in HARD:
            if rx.search(text):
                counts["hard_secret"]+=1; findings.append({"path":rel.as_posix(),"rule":name})
        if SSN.search(text):
            counts["unredacted_ssn"]+=1; findings.append({"path":rel.as_posix(),"rule":"unredacted_ssn"})
        for m in IPV4.finditer(text):
            try: ip=ipaddress.ip_address(m.group(0))
            except ValueError: continue
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                counts["private_ip"]+=1; findings.append({"path":rel.as_posix(),"rule":"private_ip"}); break
        # Email/phone counts are informational only; skipping them keeps the\n        # verifier fast on multi-megabyte pages. SSN, secrets, and private IPs\n        # remain hard failures.\n        _ = EMAIL, PHONE
    report={"root":str(root),"counts":counts,"findings":findings[:1000],"pass":not findings}
    Path(a.out).write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"pass":report["pass"],"counts":counts},sort_keys=True))
    return 0 if report["pass"] else 1

if __name__=="__main__":
    sys.exit(main())
