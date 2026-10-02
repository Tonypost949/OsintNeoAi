#!/usr/bin/env python3
"""
Remote VPS & AI Quota Sentinel
==============================
One-shot health + quota probe. Answers three questions:

  1. Is the remote VM / backend alive?        (SSH + HTTP probes)
  2. How much AI quota is left?               (GitHub / Gemini / GCP / Azure)
  3. Are local services up?                   (CLI hub, map server)

Exit codes: 0 = OK, 1 = WARN, 2 = CRITICAL
Report:     reports/sentinel/latest.json (+ timestamped copy)

Usage:
  python sentinel.py                # full probe
  python sentinel.py --only vm      # only remote checks
  python sentinel.py --only quota   # only AI quota checks
  python sentinel.py --only local   # only local service checks
  python sentinel.py --markdown     # print markdown summary only
"""

import argparse
import datetime
import json
import os
import socket
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]  # C:\OsintNeoAi
REPORT_DIR = REPO_ROOT / "reports" / "sentinel"

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SSH_TARGETS = [
    {"name": "osintneoai-vm (Azure)", "alias": "osintneoai-vm", "critical": True},
    {"name": "osint-cloud (GCP)", "alias": "osint-cloud", "critical": False},
]

HTTP_PROBES = [
    {"name": "Azure backend :10000 /health", "url": "http://57.152.82.43:10000/health", "critical": True},
    {"name": "Firebase Live Hub", "url": "https://blah-905ad.web.app", "critical": False},
    {"name": "GitHub Pages GIS", "url": "https://tonypost949.github.io/OsintNeoAi/", "critical": False},
]

LOCAL_SERVICES = [
    {"name": "OSINTNeoAiCLI hub", "port": 5052, "critical": False},
    {"name": "Map server", "port": 10000, "critical": False},
]

QUOTA_WARN_PCT = 20.0   # remaining % below this => WARN
QUOTA_CRIT_PCT = 5.0    # remaining % below this => CRITICAL

ENV_FILE = REPO_ROOT / ".env"


def env_get(key):
    """Read a key from the repo .env (no dependency on python-dotenv)."""
    try:
        for line in ENV_FILE.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if line.startswith(key + "="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    except OSError:
        pass
    return os.environ.get(key)


def run(cmd, timeout=20):
    """Run a command as a list (no shell quoting hell). Returns (rc, stdout, stderr).

    Resolves .cmd/.bat shims (gcloud, az) via shutil.which since CreateProcess
    does not apply PATHEXT.
    """
    import shutil
    exe = shutil.which(cmd[0]) or cmd[0]
    try:
        p = subprocess.run([exe] + cmd[1:], capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
        return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()
    except FileNotFoundError:
        return 127, "", f"{cmd[0]} not found"
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"


def http_probe(url, timeout=10):
    """GET a URL. Returns dict(status, code, ms, error). 404 => warn (up but missing)."""
    import time
    start = time.monotonic()
    ms = lambda: int((time.monotonic() - start) * 1000)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "osintneoai-sentinel/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            code = resp.getcode()
        return {"status": "up", "code": code, "ms": ms()}
    except urllib.error.HTTPError as e:
        status = "up" if e.code < 400 else ("warn" if e.code < 500 else "down")
        return {"status": status, "code": e.code, "ms": ms(), "error": str(e.reason)}
    except Exception as e:
        return {"status": "down", "code": None, "ms": ms(), "error": str(e)[:120]}


def port_open(host, port, timeout=3):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Section A: Remote VM checks
# ---------------------------------------------------------------------------

def check_vm():
    results = []
    for t in SSH_TARGETS:
        rc, out, err = run(
            ["ssh", "-o", "ConnectTimeout=8", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
             t["alias"], "echo OK && uptime"],
            timeout=15,
        )
        if rc == 0 and "OK" in out:
            uptime = out.replace("OK", "").strip().splitlines()[-1] if out.count("\n") else "ok"
            results.append({"check": t["name"], "kind": "ssh", "status": "up", "detail": uptime[:80], "critical": t["critical"]})
        else:
            # strip known-hosts warnings; keep the actual failure line
            lines = [l for l in (err or out).splitlines() if l.strip() and "known hosts" not in l.lower()]
            results.append({"check": t["name"], "kind": "ssh", "status": "down",
                            "detail": (lines[-1] if lines else "connect failed")[:120], "critical": t["critical"]})

    for p in HTTP_PROBES:
        r = http_probe(p["url"])
        results.append({"check": p["name"], "kind": "http", "status": r["status"],
                        "detail": f"HTTP {r['code']} in {r['ms']}ms" + (f" — {r.get('error','')}" if r.get("error") else ""),
                        "url": p["url"], "critical": p["critical"]})
    return results


# ---------------------------------------------------------------------------
# Section B: AI quota checks
# ---------------------------------------------------------------------------

def _pct(remaining, limit):
    if not limit:
        return None
    return round(100.0 * remaining / limit, 1)


def _level(pct):
    if pct is None:
        return "unknown"
    if pct <= QUOTA_CRIT_PCT:
        return "critical"
    if pct <= QUOTA_WARN_PCT:
        return "warn"
    return "ok"


def check_github():
    rc, token, _ = run(["gh", "auth", "token"], timeout=10)
    if rc != 0 or not token:
        return {"check": "GitHub API", "kind": "quota", "status": "not_auth",
                "detail": "gh not authenticated", "critical": True, "pct_remaining": None}
    try:
        req = urllib.request.Request("https://api.github.com/rate_limit",
                                     headers={"Authorization": f"Bearer {token}", "User-Agent": "sentinel"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.load(resp)
        core = data["resources"]["core"]
        pct = _pct(core["remaining"], core["limit"])
        reset = datetime.datetime.fromtimestamp(core["reset"]).strftime("%H:%M")
        return {"check": "GitHub API (core)", "kind": "quota", "status": _level(pct),
                "detail": f"{core['remaining']}/{core['limit']} remaining ({pct}%), resets {reset}",
                "pct_remaining": pct, "critical": True}
    except Exception as e:
        return {"check": "GitHub API", "kind": "quota", "status": "error", "detail": str(e)[:120],
                "critical": True, "pct_remaining": None}


def _gemini_pick_model(key):
    """Discover a usable generateContent model (names change over time)."""
    try:
        req = urllib.request.Request(
            f"https://generativelanguage.googleapis.com/v1beta/models?pageSize=50&key={key}",
            headers={"User-Agent": "sentinel"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            models = json.load(resp).get("models", [])
        for m in models:
            if "generateContent" in m.get("supportedGenerationMethods", []):
                return m["name"].removeprefix("models/")
    except Exception:
        pass
    return "gemini-2.5-flash"  # fallback candidate


def check_gemini():
    key = env_get("GEMINI_API_KEY")
    if not key:
        return {"check": "Gemini API", "kind": "quota", "status": "not_auth",
                "detail": "GEMINI_API_KEY missing from .env", "critical": True, "pct_remaining": None}

    body = json.dumps({"contents": [{"parts": [{"text": "ping"}]}],
                       "generationConfig": {"maxOutputTokens": 1}}).encode()
    headers, code = {}, None

    for attempt_model in dict.fromkeys([_gemini_pick_model(key), "gemini-3.8-flash", "gemini-flash-latest"]):
        url = (f"https://generativelanguage.googleapis.com/v1beta/models/{attempt_model}"
               f":generateContent?key={key}")
        req = urllib.request.Request(url, data=body, method="POST",
                                     headers={"Content-Type": "application/json", "User-Agent": "sentinel"})
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                code = resp.getcode()
                headers = {k.lower(): v for k, v in resp.headers.items()}
                model = attempt_model
                break
        except urllib.error.HTTPError as e:
            code = e.code
            headers = {k.lower(): v for k, v in e.headers.items()}
            if code == 429:
                return {"check": "Gemini API", "kind": "quota", "status": "critical",
                        "detail": "429 RATE LIMITED — quota exhausted", "pct_remaining": 0.0, "critical": True}
            if code == 404:
                continue  # try next candidate model
            if code == 402:
                return {"check": "Gemini API", "kind": "quota", "status": "critical",
                        "detail": "402 PAYMENT REQUIRED — project has no Gemini quota/billing enabled",
                        "pct_remaining": 0.0, "critical": True}
            if code >= 500:
                return {"check": "Gemini API", "kind": "quota", "status": "error",
                        "detail": f"HTTP {code} on {attempt_model}", "pct_remaining": None, "critical": True}
        except Exception as e:
            return {"check": "Gemini API", "kind": "quota", "status": "error", "detail": str(e)[:120],
                    "pct_remaining": None, "critical": True}

    # Gemini returns x-ratelimit-* headers when available
    lim = headers.get("x-ratelimit-limit-requests")
    rem = headers.get("x-ratelimit-remaining-requests")
    tok_lim = headers.get("x-ratelimit-limit-tokens")
    tok_rem = headers.get("x-ratelimit-remaining-tokens")
    if lim and rem:
        pct = _pct(float(rem), float(lim))
        detail = f"{rem}/{lim} requests/min ({pct}%)"
        if tok_lim and tok_rem:
            detail += f"; {tok_rem}/{tok_lim} tokens/min"
        return {"check": "Gemini API", "kind": "quota", "status": _level(pct),
                "detail": detail, "pct_remaining": pct, "critical": True}
    if code == 200:
        return {"check": "Gemini API", "kind": "quota", "status": "ok",
                "detail": f"API alive via {model} (HTTP 200, no ratelimit headers exposed)",
                "pct_remaining": None, "critical": True}
    return {"check": "Gemini API", "kind": "quota", "status": "unknown",
            "detail": f"HTTP {code} on all candidate models", "pct_remaining": None, "critical": True}


def check_gcp_quotas():
    rc, out, err = run(["gcloud", "compute", "project-info", "describe", "--format=json"], timeout=25)
    if rc != 0:
        return [{"check": "GCP quotas", "kind": "quota", "status": "not_auth" if "credentials" in err.lower() or "auth" in err.lower() else "error",
                 "detail": (err or out)[:120], "pct_remaining": None, "critical": False}]
    try:
        data = json.loads(out)
        quotas = {q["metric"]: q for q in data.get("quotas", [])}
        interesting = ["CPUS", "DISKS_TOTAL_GB", "IN_USE_ADDRESSES"]
        results = []
        for metric in interesting:
            q = quotas.get(metric)
            if not q:
                continue
            limit = float(q.get("limit", 0) or 0)
            usage = float(q.get("usage", 0) or 0)
            pct = _pct(limit - usage, limit) if limit else None
            results.append({"check": f"GCP {metric}", "kind": "quota", "status": _level(pct),
                            "detail": f"usage {usage:g} / limit {limit:g} ({pct}% free)",
                            "pct_remaining": pct, "critical": False})
        return results or [{"check": "GCP quotas", "kind": "quota", "status": "unknown",
                            "detail": "no quota metrics returned", "pct_remaining": None, "critical": False}]
    except Exception as e:
        return [{"check": "GCP quotas", "kind": "quota", "status": "error", "detail": str(e)[:120],
                 "pct_remaining": None, "critical": False}]


def check_azure():
    rc, out, err = run(["az", "account", "show", "--query", "name", "-o", "tsv"], timeout=20)
    if rc != 0 or not out:
        return [{"check": "Azure", "kind": "quota", "status": "not_auth",
                 "detail": "az not logged in (run: az login)", "pct_remaining": None, "critical": False}]
    results = [{"check": "Azure account", "kind": "quota", "status": "ok",
                "detail": f"logged in: {out}", "pct_remaining": None, "critical": False}]
    rc, out, err = run(["az", "vm", "list-ip-addresses", "-o", "json"], timeout=30)
    if rc == 0:
        try:
            vms = json.loads(out)
            ips = [n["virtualMachine"]["ipAddress"] for v in vms for n in v.get("network", {}).get("ipAddresses", [])]
            results.append({"check": "Azure VMs", "kind": "quota", "status": "ok" if ips else "warn",
                            "detail": f"{len(vms)} VM(s): {', '.join(ips) if ips else 'no public IPs'}",
                            "pct_remaining": None, "critical": False})
        except Exception:
            pass
    return results


def check_quota():
    return [check_github(), check_gemini()] + check_gcp_quotas() + check_azure()


# ---------------------------------------------------------------------------
# Section C: Local services
# ---------------------------------------------------------------------------

def check_local():
    results = []
    for s in LOCAL_SERVICES:
        up = port_open("127.0.0.1", s["port"])
        results.append({"check": s["name"], "kind": "local", "status": "up" if up else "down",
                        "detail": f"127.0.0.1:{s['port']} {'listening' if up else 'not listening'}",
                        "port": s["port"], "critical": s["critical"]})
    return results


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

STATUS_RANK = {"ok": 0, "up": 0, "unknown": 1, "not_auth": 1, "warn": 1, "error": 2, "down": 2, "critical": 2}


def overall_status(results):
    worst, worst_rank = "ok", 0
    for r in results:
        rank = STATUS_RANK.get(r["status"], 1)
        if rank == 1 and r.get("critical"):
            rank = 2  # critical check in unknown/not_auth state counts as severe
        if rank > worst_rank:
            worst, worst_rank = r["status"], rank
    return {0: "OK", 1: "WARN", 2: "CRITICAL"}[min(worst_rank, 2)]


def to_markdown(report):
    lines = [f"# Sentinel Report — {report['timestamp']}", "",
             f"**Overall: {report['overall']}**", ""]
    for section, title in (("vm", "Remote VM & Endpoints"), ("quota", "AI / Cloud Quota"),
                           ("local", "Local Services")):
        lines.append(f"## {title}")
        lines.append("")
        lines.append("| Check | Status | Detail |")
        lines.append("|---|---|---|")
        for r in report["results"].get(section, []):
            icon = {"ok": "🟢", "up": "🟢", "warn": "🟡", "down": "🔴", "critical": "🔴",
                    "error": "🔴", "not_auth": "⚪", "unknown": "⚪"}.get(r["status"], "⚪")
            detail = r["detail"].replace("|", "/")
            lines.append(f"| {r['check']} | {icon} {r['status']} | {detail} |")
        lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Remote VPS & AI Quota Sentinel")
    ap.add_argument("--only", choices=["vm", "quota", "local"], help="run one section only")
    ap.add_argument("--markdown", action="store_true", help="print markdown report only")
    ap.add_argument("--no-save", action="store_true", help="do not write report files")
    args = ap.parse_args()

    sections = ["vm", "quota", "local"] if not args.only else [args.only]
    results = {}
    if "vm" in sections:
        results["vm"] = check_vm()
    if "quota" in sections:
        results["quota"] = check_quota()
    if "local" in sections:
        results["local"] = check_local()

    flat = [r for rs in results.values() for r in rs]
    report = {
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "overall": overall_status(flat),
        "results": results,
        "thresholds": {"warn_pct": QUOTA_WARN_PCT, "critical_pct": QUOTA_CRIT_PCT},
    }

    if not args.no_save:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        stamp = report["timestamp"].replace(":", "").replace("-", "").replace("T", "_")
        (REPORT_DIR / f"quota_report_{stamp}.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        (REPORT_DIR / "latest.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        (REPORT_DIR / "latest.md").write_text(to_markdown(report), encoding="utf-8")

    if args.markdown:
        print(to_markdown(report))
    else:
        for section, rs in results.items():
            print(f"\n[{section.upper()}]")
            for r in rs:
                print(f"  {r['status'].upper():9s} {r['check']}: {r['detail']}")
        print(f"\nOVERALL: {report['overall']}")
        if not args.no_save:
            print(f"Report:  {REPORT_DIR / 'latest.md'}")

    return {"OK": 0, "WARN": 1, "CRITICAL": 2}[report["overall"]]


if __name__ == "__main__":
    sys.exit(main())
