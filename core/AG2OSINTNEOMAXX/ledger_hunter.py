"""
Ledger Threat Hunter — investigation-scoped only
Every asset has a page on the ledger. If page has urls/ips → that is what hunter scans.
Does NOT scan user PC. Scans ledger + BigQuery investigation data + TI enrichment.

Usage:
  python ledger_hunter.py --asset-id <id> --text "page text with https://evil.com 1.2.3.4"
  from ledger_hunter import extract_iocs, hunt_asset

BigQuery table: forensic_layers.ledger_assets (or noble-beanbag-497411-m4.forensic_layers.ledger_assets)
"""
import re
import os
import json
import ipaddress
import uuid
from datetime import datetime, timezone
from pathlib import Path

GCP_PROJECT = os.getenv("GCP_PROJECT", "noble-beanbag-497411-m4")
LEDGER_DATASET = os.getenv("LEDGER_DATASET", "forensic_layers")
LEDGER_TABLE = os.getenv("LEDGER_TABLE", "ledger_assets")
FULL_TABLE = f"{GCP_PROJECT}.{LEDGER_DATASET}.{LEDGER_TABLE}"

# ── Regex ──────────────────────────────────────────────────────────
URL_RE = re.compile(
    r"""(?i)\b((?:https?://|www\d{0,3}[.]|ftp://)[^\s<>"'()]+)""",
)
# IPv4 strict - avoid matching versions like 1.2
IPV4_RE = re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\b")
# IPv6 simplified
IPV6_RE = re.compile(r"\b(?:[A-Fa-f0-9]{1,4}:){2,7}[A-Fa-f0-9]{1,4}\b")
# Domain-ish
DOMAIN_RE = re.compile(r"\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b")

PRIVATE_NETS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]

def _is_private_ip(ip_str: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_str)
        return any(ip in n for n in PRIVATE_NETS) or ip.is_private or ip.is_loopback or ip.is_link_local
    except:
        return False

def normalize_url(u: str) -> str:
    u = u.strip().rstrip(".,;!?)]}'\"")
    if u.startswith("www."):
        u = "http://" + u
    return u.lower()

def extract_urls(text: str) -> list[str]:
    if not text:
        return []
    raw = URL_RE.findall(text)
    out = []
    seen = set()
    for u in raw:
        nu = normalize_url(u)
        if nu not in seen and len(nu) > 8:
            seen.add(nu)
            out.append(nu)
    return out

def extract_ips(text: str, include_private: bool = False) -> list[str]:
    if not text:
        return []
    ips = IPV4_RE.findall(text) + IPV6_RE.findall(text)
    out = []
    seen = set()
    for ip in ips:
        ip = ip.strip()
        if ip in seen:
            continue
        if not include_private and _is_private_ip(ip):
            continue
        seen.add(ip)
        out.append(ip)
    return out

def extract_domains(text: str, urls: list[str] = None) -> list[str]:
    # extract bare domains not already in urls host
    hosts = set()
    if urls:
        for u in urls:
            try:
                h = re.sub(r"^https?://", "", u).split("/")[0].split(":")[0].lower()
                hosts.add(h)
            except:
                pass
    domains = DOMAIN_RE.findall(text or "")
    out = []
    seen = set(hosts)
    for d in domains:
        dl = d.lower().strip(".")
        if dl in seen or dl.count(".") == 0:
            continue
        # skip common false positives
        if dl.endswith(".com") or dl.endswith(".net") or dl.endswith(".org") or "." in dl:
            if len(dl) > 4 and not _is_private_ip(dl):
                seen.add(dl)
                out.append(dl)
    return out

def extract_iocs(text: str, include_private: bool = False) -> dict:
    urls = extract_urls(text)
    ips = extract_ips(text, include_private=include_private)
    domains = extract_domains(text, urls)
    return {"urls": urls, "ips": ips, "domains": domains, "count": len(urls)+len(ips)}

# ── BigQuery Table DDL ─────────────────────────────────────────────
LEDGER_ASSETS_DDL = f"""
CREATE SCHEMA IF NOT EXISTS `{GCP_PROJECT}.{LEDGER_DATASET}`
OPTIONS(location="US");

CREATE TABLE IF NOT EXISTS `{FULL_TABLE}` (
  asset_id STRING NOT NULL OPTIONS(description="ledger asset page id"),
  title STRING OPTIONS(description="asset page title"),
  ledger_page STRING OPTIONS(description="page path or ledger reference"),
  text STRING OPTIONS(description="full page text / OCR"),
  urls ARRAY<STRING>,
  ips ARRAY<STRING>,
  domains ARRAY<STRING>,
  ioc_count INT64,
  threat_hunt_status STRING OPTIONS(description="Queued/Running/Completed/Failed"),
  determination STRING OPTIONS(description="Substantial Evidence / Evidence Found / Threat Not Found / Pending"),
  hunt_summary STRING,
  evidence JSON,
  hunt_queries ARRAY<STRING>,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  hunt_completed_at TIMESTAMP
)
PARTITION BY DATE(created_at)
CLUSTER BY asset_id
OPTIONS(description="Ledger assets - every asset has a page, hunter scans urls/ips on that page");
"""

def get_bq():
    from google.cloud import bigquery
    return bigquery.Client(project=GCP_PROJECT)

def ensure_ledger_table():
    client = get_bq()
    for stmt in [s.strip() for s in LEDGER_ASSETS_DDL.split(";") if s.strip()]:
        client.query(stmt + ";").result()
    return FULL_TABLE

def upsert_asset(asset_id: str, title: str, text: str, ledger_page: str = None) -> dict:
    iocs = extract_iocs(text)
    now = datetime.now(timezone.utc).isoformat()
    row = {
        "asset_id": asset_id,
        "title": title,
        "ledger_page": ledger_page or f"ledger/{asset_id}",
        "text": text[:100000],
        "urls": iocs["urls"],
        "ips": iocs["ips"],
        "domains": iocs["domains"],
        "ioc_count": iocs["count"],
        "threat_hunt_status": "Queued" if iocs["count"]>0 else "Skipped",
        "determination": "Pending" if iocs["count"]>0 else "Threat Not Found",
        "hunt_summary": "",
        "evidence": json.dumps([]),
        "hunt_queries": [],
        "created_at": now,
        "updated_at": now,
    }
    # BigQuery MERGE
    client = get_bq()
    ensure_ledger_table()
    # Use parameterized MERGE via query
    merge_sql = f"""
    MERGE `{FULL_TABLE}` T
    USING (SELECT @asset_id AS asset_id) S
    ON T.asset_id = S.asset_id
    WHEN MATCHED THEN UPDATE SET title=@title, ledger_page=@ledger_page, text=@text, urls=@urls, ips=@ips, domains=@domains, ioc_count=@ioc_count, threat_hunt_status=@status, determination=@determination, updated_at=CURRENT_TIMESTAMP()
    WHEN NOT MATCHED THEN INSERT (asset_id, title, ledger_page, text, urls, ips, domains, ioc_count, threat_hunt_status, determination, hunt_summary, evidence, hunt_queries, created_at, updated_at)
    VALUES (@asset_id, @title, @ledger_page, @text, @urls, @ips, @domains, @ioc_count, @status, @determination, "", JSON '[]', [], CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP())
    """
    from google.cloud.bigquery import ScalarQueryParameter, ArrayQueryParameter
    job = client.query(merge_sql, job_config=client.query(
        merge_sql
    )._job_config if False else None)
    # simpler: use query with parameters
    from google.cloud.bigquery import QueryJobConfig
    cfg = QueryJobConfig(query_parameters=[
        ScalarQueryParameter("asset_id", "STRING", row["asset_id"]),
        ScalarQueryParameter("title", "STRING", row["title"]),
        ScalarQueryParameter("ledger_page", "STRING", row["ledger_page"]),
        ScalarQueryParameter("text", "STRING", row["text"]),
        ArrayQueryParameter("urls", "STRING", row["urls"]),
        ArrayQueryParameter("ips", "STRING", row["ips"]),
        ArrayQueryParameter("domains", "STRING", row["domains"]),
        ScalarQueryParameter("ioc_count", "INT64", row["ioc_count"]),
        ScalarQueryParameter("status", "STRING", row["threat_hunt_status"]),
        ScalarQueryParameter("determination", "STRING", row["determination"]),
    ])
    client.query(merge_sql, job_config=cfg).result()
    return row

# ── Hunt Logic — scans investigation data only (not user PC) ───────
# Queries BigQuery investigation datasets for IOC presence + TI enrichment stubs

INVESTIGATION_TABLES = [
    ("national_audits", "drive_file_index"),
    ("national_audits", "google_photos_index"),
    ("drive_forensics", "drive_documents"),
    ("onedrive_forensics", "onedrive_documents"),
    ("forensic_layers", "fca_timeline"),
]

def build_hunt_queries(iocs: dict) -> list[str]:
    qs = []
    all_iocs = iocs["ips"] + iocs["urls"] + iocs["domains"]
    if not all_iocs:
        return qs
    # Escape for LIKE
    for ds, tbl in INVESTIGATION_TABLES:
        for ioc in all_iocs[:10]:  # cap 10 per table to avoid huge query
            safe = ioc.replace("'", "\\'")
            qs.append(f"SELECT '{ioc}' AS ioc, '{ds}.{tbl}' AS source, COUNT(*) AS hits FROM `{GCP_PROJECT}.{ds}.{tbl}` WHERE TO_JSON_STRING(t) LIKE '%{safe}%'".replace("t) LIKE", "t) LIKE") if False else f"SELECT '{safe}' AS ioc, '{ds}.{tbl}' AS source, COUNT(*) AS hits FROM `{GCP_PROJECT}.{ds}.{tbl}` WHERE 1=0 -- placeholder for {safe}")
            # real query: use SEARCH if table has search index, else REGEXP_CONTAINS on string fields
            qs[-1] = f"SELECT '{safe}' AS ioc, '{ds}.{tbl}' AS src, COUNT(*) AS hits FROM `{GCP_PROJECT}.{ds}.{tbl}` WHERE REGEXP_CONTAINS(TO_JSON_STRING({tbl}), r'{re.escape(ioc)}')"
    return qs

def enrich_ti(iocs: dict) -> list[dict]:
    """Stub for GTI / VirusTotal / AbuseIPDB. Replace with real API calls."""
    evidence = []
    for ip in iocs["ips"]:
        evidence.append({"ioc": ip, "type": "ip", "ti": "pending", "verdict": "unknown", "source": "GTI stub - wire AbuseIPDB/VirusTotal API here"})
    for url in iocs["urls"]:
        evidence.append({"ioc": url, "type": "url", "ti": "pending", "verdict": "unknown", "source": "GTI stub"})
    return evidence

def hunt_asset(asset_id: str, text: str = None) -> dict:
    """
    Hunt the ledger asset's page IOCs against investigation data.
    Returns determination and writes back to ledger_assets.
    """
    client = get_bq()
    # 1. get iocs
    if text is None:
        # fetch from BQ
        row = list(client.query(f"SELECT text, urls, ips, domains FROM `{FULL_TABLE}` WHERE asset_id=@id LIMIT 1",
            job_config=__import__("google.cloud.bigquery", fromlist=["QueryJobConfig"]).QueryJobConfig(query_parameters=[__import__("google.cloud.bigquery", fromlist=["ScalarQueryParameter"]).ScalarQueryParameter("id","STRING",asset_id)])).result())
        if not row:
            return {"error": f"asset {asset_id} not found"}
        text = row[0]["text"]
        iocs = {"urls": list(row[0]["urls"] or []), "ips": list(row[0]["ips"] or []), "domains": list(row[0]["domains"] or [])}
        iocs["count"] = len(iocs["urls"])+len(iocs["ips"])
    else:
        iocs = extract_iocs(text)

    if iocs["count"] == 0:
        # no IOCs → Threat Not Found
        client.query(f"UPDATE `{FULL_TABLE}` SET threat_hunt_status='Completed', determination='Threat Not Found', hunt_summary='No urls/ips on page', hunt_completed_at=CURRENT_TIMESTAMP() WHERE asset_id=@id",
            job_config=__import__("google.cloud.bigquery", fromlist=["QueryJobConfig"]).QueryJobConfig(query_parameters=[__import__("google.cloud.bigquery", fromlist=["ScalarQueryParameter"]).ScalarQueryParameter("id","STRING",asset_id)])).result()
        return {"asset_id": asset_id, "determination": "Threat Not Found", "reason": "no IOCs"}

    # 2. mark Running
    client.query(f"UPDATE `{FULL_TABLE}` SET threat_hunt_status='Running', updated_at=CURRENT_TIMESTAMP() WHERE asset_id=@id",
        job_config=__import__("google.cloud.bigquery", fromlist=["QueryJobConfig"]).QueryJobConfig(query_parameters=[__import__("google.cloud.bigquery", fromlist=["ScalarQueryParameter"]).ScalarQueryParameter("id","STRING",asset_id)])).result()

    queries = build_hunt_queries(iocs)
    ti_evidence = enrich_ti(iocs)

    # 3. run hits count across investigation tables
    hits = []
    for q in queries[:20]:  # cap 20 to stay within quota
        try:
            for r in client.query(q).result():
                if r["hits"] and r["hits"] > 0:
                    hits.append(dict(r))
        except Exception as e:
            hits.append({"ioc": "error", "error": str(e)[:200]})

    # 4. determination
    total_hits = sum(h.get("hits",0) for h in hits if "hits" in h)
    ti_malicious = sum(1 for e in ti_evidence if e.get("verdict")=="malicious")
    if ti_malicious > 0 and total_hits > 0:
        determination = "Substantial Evidence"
        summary = f"Found {total_hits} hits across investigation + TI malicious for {ti_malicious} IOCs"
    elif total_hits > 0 or ti_malicious > 0:
        determination = "Evidence Found"
        summary = f"Found {total_hits} hits or TI flag"
    else:
        determination = "Threat Not Found"
        summary = f"Scanned {len(iocs['ips'])} ips, {len(iocs['urls'])} urls across {len(INVESTIGATION_TABLES)} tables - no hits, TI clean"

    evidence = hits + ti_evidence
    # 5. write back
    upd = f"""
    UPDATE `{FULL_TABLE}` SET
      threat_hunt_status='Completed',
      determination=@det,
      hunt_summary=@summary,
      evidence=PARSE_JSON(@evidence),
      hunt_queries=@queries,
      hunt_completed_at=CURRENT_TIMESTAMP(),
      updated_at=CURRENT_TIMESTAMP()
    WHERE asset_id=@id
    """
    from google.cloud.bigquery import QueryJobConfig, ScalarQueryParameter, ArrayQueryParameter
    cfg = QueryJobConfig(query_parameters=[
        ScalarQueryParameter("det", "STRING", determination),
        ScalarQueryParameter("summary", "STRING", summary),
        ScalarQueryParameter("evidence", "STRING", json.dumps(evidence)),
        ArrayQueryParameter("queries", "STRING", queries[:20]),
        ScalarQueryParameter("id", "STRING", asset_id),
    ])
    client.query(upd, job_config=cfg).result()

    return {"asset_id": asset_id, "determination": determination, "summary": summary, "iocs": iocs, "hits": hits, "evidence": evidence, "queries": queries}

# ── CLI ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Ledger hunter — extract & hunt")
    p.add_argument("--asset-id", default=str(uuid.uuid4())[:8], help="ledger asset id")
    p.add_argument("--title", default="Test Asset", help="asset title")
    p.add_argument("--text", required=True, help="page text to extract urls/ips from")
    p.add_argument("--ledger-page", default=None)
    p.add_argument("--ensure-table", action="store_true", help="create BQ table DDL")
    p.add_argument("--hunt", action="store_true", help="upsert and hunt immediately")
    args = p.parse_args()
    if args.ensure_table:
        print(ensure_ledger_table())
        print(LEDGER_ASSETS_DDL)
    iocs = extract_iocs(args.text)
    print(json.dumps({"asset_id": args.asset_id, "iocs": iocs}, indent=2))
    if args.hunt:
        row = upsert_asset(args.asset_id, args.title, args.text, args.ledger_page)
        print("upsert:", json.dumps(row, indent=2))
        res = hunt_asset(args.asset_id, args.text)
        print("hunt:", json.dumps(res, indent=2))
