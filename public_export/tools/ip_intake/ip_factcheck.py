#!/usr/bin/env python3
"""ip_factcheck.py — passive fact-checking for a list of IP addresses.

Sources (all passive, no port scanning / no packets to the target):
  * RDAP via rdap.org bootstrap (registry truth: netblock owner, range, abuse contact)
  * Team Cymru whois (origin AS, AS name, BGP prefix, country, registry)
  * PTR via `dig -x` (reverse DNS)
  * Shodan InternetDB (free, passive: known ports, hostnames, tags, CVEs)

Outputs CSV + JSONL + a Markdown fact-check report with an automated
classification (CDN edge vs cloud vs hosting vs ISP vs government vs unknown)
and provenance (query timestamps, source URLs).

Usage:
  python3 ip_factcheck.py --ips-file ips.txt --out DIR
  python3 ip_factcheck.py --rollup ip_rollup.csv --top 30 --extra "[IP_REDACTED],[IP_REDACTED]" --out DIR
"""

import argparse
import csv
import json
import re
import socket
import subprocess
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

TOOL_VERSION = "1.0.0"
UA = "osintneoai-ip-factcheck/1.0 (passive attribution)"

KIND_RULES = [
    ("cloudflare", "CDN edge (Cloudflare anycast)"),
    ("fastly", "CDN edge (Fastly)"),
    ("akamai", "CDN edge (Akamai)"),
    ("cloudfront", "CDN edge (CloudFront)"),
    ("google", "Cloud (Google)"),
    ("microsoft", "Cloud (Microsoft Azure)"),
    ("azure", "Cloud (Microsoft Azure)"),
    ("amazon", "Cloud (AWS)"),
    ("aws", "Cloud (AWS)"),
    ("github", "Hosting (GitHub Pages/Fastly)"),
    ("wpengine", "Managed hosting (WP Engine)"),
    ("granicus", "Gov SaaS (Granicus)"),
    ("digitalocean", "VPS hosting (DigitalOcean)"),
    ("linode", "VPS hosting (Linode)"),
    ("ovh", "Hosting (OVH)"),
    ("hetzner", "Hosting (Hetzner)"),
    ("leaseweb", "Hosting (Leaseweb)"),
    ("level3", "ISP/backbone (Lumen)"),
    ("lumen", "ISP/backbone (Lumen)"),
    ("cogent", "ISP/backbone (Cogent)"),
    ("comcast", "ISP (Comcast)"),
    ("telefonica", "ISP (Telefonica)"),
    ("vivo", "ISP (Vivo/Telefonica)"),
    ("charter", "ISP (Charter/Spectrum)"),
    ("at&t", "ISP (AT&T)"),
    ("verizon", "ISP (Verizon)"),
    ("cox", "ISP (Cox)"),
]

GOV_RE = re.compile(r"\b(city|county|state|municipal|government|gov|sheriff|police|department|district|authority|agency)\b", re.I)


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def http_json(url, timeout=12):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", errors="ignore"))


def cymru_lookup(ips):
    """Batch whois to Team Cymru. Returns {ip: row dict}."""
    out = {}
    try:
        s = socket.create_connection(("whois.cymru.com", 43), timeout=20)
    except OSError as e:
        print(f"[cymru] connection failed: {e}", file=sys.stderr)
        return out
    try:
        payload = "begin\nverbose\n" + "\n".join(ips) + "\nend\n"
        s.sendall(payload.encode())
        data = b""
        while True:
            chunk = s.recv(655**)
            if not chunk:
                break
            data += chunk
    finally:
        s.close()
    for line in data.decode("utf-8", errors="ignore").splitlines():
        if "|" not in line or line.startswith("AS "):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 7:
            continue
        asn, ip, prefix, cc, registry, allocated, asname = parts[:7]
        out[ip] = {
            "asn": asn, "bgp_prefix": prefix, "cc": cc,
            "registry": registry, "allocated": allocated, "as_name": asname,
        }
    return out


def _vcard_flat(v):
    """Flatten a jCard into (fn, org, emails)."""
    fn, org, emails = "", "", []
    try:
        arr = v.get("vcardArray", [None, []])[1]
        for item in arr:
            if len(item) < 4:
                continue
            key, val = item[0], item[3]
            if key == "fn":
                fn = val if isinstance(val, str) else str(val)
            elif key == "org":
                org = " / ".join(val) if isinstance(val, list) else str(val)
            elif key == "email":
                emails.append(val if isinstance(val, str) else str(val))
    except Exception:
        pass
    return fn, org, emails


def _walk_entities(entities, fns, orgs, emails, depth=0):
    if depth > 4:
        return
    for ent in entities or []:
        fn, org, em = _vcard_flat(ent)
        if fn:
            fns.append(fn)
        if org:
            orgs.append(org)
        emails.extend(em)
        _walk_entities(ent.get("entities"), fns, orgs, emails, depth + 1)


def rdap_lookup(ip):
    try:
        d = http_json(f"https://rdap.org/ip/{ip}", timeout=15)
    except Exception as e:
        return {"error": str(e)[:160]}
    fns, orgs, emails = [], [], []
    _walk_entities(d.get("entities"), fns, orgs, emails)
    return {
        "name": d.get("name") or "",
        "handle": d.get("handle") or "",
        "country": d.get("country") or "",
        "start": d.get("startAddress") or "",
        "end": d.get("endAddress") or "",
        "type": d.get("type") or "",
        "orgs": list(dict.fromkeys(orgs))[:4],
        "fns": list(dict.fromkeys(fns))[:4],
        "emails": list(dict.fromkeys(emails))[:3],
        "rdap_url": f"https://rdap.org/ip/{ip}",
    }


def ptr_lookup(ip):
    try:
        r = subprocess.run(["dig", "+short", "-x", ip], capture_output=True, text=True, timeout=8)
        names = [x.strip().rstrip(".") for x in r.stdout.splitlines() if x.strip()]
        return ", ".join(names[:4])
    except Exception:
        return ""


def internetdb(ip):
    try:
        return http_json(f"https://internetdb.shodan.io/{ip}", timeout=10)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {}
        return {"error": f"http {e.code}"}
    except Exception as e:
        return {"error": str(e)[:120]}


def classify(row):
    hay = " ".join(str(row.get(k) or "") for k in ("as_name", "rdap_name", "rdap_org")).lower()
    for key, label in KIND_RULES:
        if key in hay:
            return label
    if GOV_RE.search(hay):
        return "Government / municipal network"
    if row.get("asn") and row["asn"] not in ("NA", "0"):
        return "Other network (see ASN)"
    return "Unannounced / unknown"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ips-file")
    ap.add_argument("--rollup")
    ap.add_argument("--top", type=int, default=30)
    ap.add_argument("--extra", default="")
    ap.add_argument("--out", required=True)
    ap.add_argument("--sleep", type=float, default=0.4)
    args = ap.parse_args()

    ips = []
    if args.rollup:
        with open(args.rollup) as f:
            rows = list(csv.DictReader(f))
        n = 0
        for r in rows:
            if n >= args.top:
                break
            ip = r.get("ip", "")
            if r.get("class", "public") != "public":
                continue          # skip private/loopback/reserved noise
            if ip in ("[IP_REDACTED]",):
                continue          # documentation placeholder
            if re.match(r"^\d+\.\d+\.\d+\.(0|255)$", ip):
                continue          # network / broadcast addresses
            ips.append(ip)
            n += 1
    if args.ips_file:
        for line in Path(args.ips_file).read_text().splitlines():
            line = line.strip()
            if re.match(r"^[0-9a-fA-F:.]+$", line):
                ips.append(line)
    for x in args.extra.split(","):
        x = x.strip()
        if x:
            ips.append(x)
    # dedupe preserving order, validate
    seen, ordered = set(), []
    for ip in ips:
        if ip in seen:
            continue
        try:
            socket.inet_pton(socket.AF_INET, ip)
        except OSError:
            try:
                socket.inet_pton(socket.AF_INET6, ip)
            except OSError:
                continue
        seen.add(ip)
        ordered.append(ip)
    if not ordered:
        print("no valid IPs given", file=sys.stderr)
        sys.exit(1)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    stamp = now()
    print(f"[factcheck] {len(ordered)} IPs, sources: RDAP + Team Cymru + PTR + InternetDB", file=sys.stderr)

    cymru = cymru_lookup(ordered)
    rows = []
    for i, ip in enumerate(ordered, 1):
        r = {"ip": ip, "checked_at": stamp}
        r.update(cymru.get(ip, {}))
        rd = rdap_lookup(ip)
        r["rdap_name"] = rd.get("name", "")
        r["rdap_handle"] = rd.get("handle", "")
        r["rdap_country"] = rd.get("country", "")
        r["rdap_range"] = f"{rd.get('start','')}-{rd.get('end','')}" if rd.get("start") else ""
        r["rdap_org"] = " / ".join(rd.get("orgs") or [])
        r["rdap_contact"] = ", ".join((rd.get("emails") or [])[:2])
        r["rdap_error"] = rd.get("error", "")
        r["ptr"] = ptr_lookup(ip)
        db = internetdb(ip)
        r["internetdb_ports"] = ",".join(str(p) for p in (db.get("ports") or [])[:20])
        r["internetdb_hostnames"] = ", ".join((db.get("hostnames") or [])[:5])
        r["internetdb_tags"] = ", ".join((db.get("tags") or [])[:8])
        vulns = db.get("vulns") or {}
        if isinstance(vulns, dict):
            vkeys = list(vulns.keys())
        elif isinstance(vulns, list):
            vkeys = [str(x) for x in vulns]
        else:
            vkeys = []
        r["internetdb_vulns"] = ",".join(vkeys[:8])
        r["kind"] = classify(r)
        rows.append(r)
        print(f"  [{i}/{len(ordered)}] {ip} -> {r.get('asn','?')} {r.get('as_name','')[:40]} | {r['kind']}", file=sys.stderr)
        time.sleep(args.sleep)

    fields = ["ip", "checked_at", "asn", "as_name", "bgp_prefix", "cc", "registry", "allocated",
              "rdap_name", "rdap_handle", "rdap_country", "rdap_range", "rdap_org", "rdap_contact", "rdap_error",
              "ptr", "internetdb_ports", "internetdb_hostnames", "internetdb_tags", "internetdb_vulns", "kind"]
    with open(out / "factcheck.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    with open(out / "factcheck.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # ---- markdown report ----
    from collections import Counter
    kinds = Counter(r["kind"] for r in rows)
    lines = []
    lines.append(f"# IP Fact-Check Report - passive attribution\n")
    lines.append(f"- **Generated (UTC):** {stamp}")
    lines.append(f"- **Tool:** ip_factcheck {TOOL_VERSION}")
    lines.append(f"- **IPs checked:** {len(rows)}")
    lines.append(f"- **Sources:** RDAP (rdap.org), Team Cymru whois, PTR (dig -x), Shodan InternetDB (passive)")
    lines.append(f"- **No active probing:** no SYN/port scans and no packets sent to targets.\n")
    lines.append("## Classification summary\n")
    lines.append("| Kind | Count |")
    lines.append("|------|-------|")
    for k, c in kinds.most_common():
        lines.append(f"| {k} | {c} |")
    lines.append("")
    lines.append("## Per-IP results\n")
    lines.append("| IP | ASN | AS name | Kind | PTR | RDAP netname | Country | Ports (InternetDB) |")
    lines.append("|----|-----|---------|------|-----|--------------|---------|--------------------|")
    for r in rows:
        ptr = (r["ptr"] or "-")[:45]
        ports = (r["internetdb_ports"] or "-")[:40]
        lines.append(f'| {r["ip"]} | {r.get("asn","-")} | {(r.get("as_name") or "-")[:45]} | {r["kind"]} | {ptr} | {r.get("rdap_name") or "-"} | {r.get("rdap_country") or "-"} | {ports} |')
    lines.append("")
    lines.append("## Caveats\n")
    lines.append("- CDN/anycast IPs (Cloudflare, Fastly, Akamai, CloudFront, GitHub Pages) are shared front doors; they do NOT identify the origin server behind them.")
    lines.append("- InternetDB is Shodan's passive cache; absence of ports means 'not observed', not 'closed'.")
    lines.append("- RDAP is the registry source of truth for allocation; the registrant org may be an ISP or host, not the ultimate customer.")
    lines.append("- ASN/prefix data from Team Cymru; BGP prefix shows the routed block, not the customer assignment.")
    (out / "IP_FACTCHECK_REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"[factcheck] outputs -> {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
