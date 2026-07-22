"""
city_ip_geolocation_v2.py
=========================
Geolocates IP addresses using:
  1. MaxMind GeoLite2-City.mmdb (local, no API key, fast)
  2. ip-api.com REST API       (fallback, free tier, no key)

Stores results in BigQuery:
  project-743aab84-f9a5-4ec7-954.national_audits.ip_geolocation_index

Usage:
    python city_ip_geolocation_v2.py --ips 8.8.8.8 1.1.1.1
    python city_ip_geolocation_v2.py --file ips.txt
    python city_ip_geolocation_v2.py --city "Huntington Beach"
    python city_ip_geolocation_v2.py --scan-california-cities
"""

import argparse
import json
import os
import sys
import time
import socket
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

# ── Configuration ────────────────────────────────────────────────────────────
PROJECT_ID       = "project-743aab84-f9a5-4ec7-954"
BQ_DATASET       = "national_audits"
BQ_TABLE_GEO     = f"{PROJECT_ID}.{BQ_DATASET}.ip_geolocation_index"
BQ_TABLE_INV     = f"{PROJECT_ID}.{BQ_DATASET}.city_ip_inventory"
MMDB_PATH        = os.path.join(os.path.dirname(__file__), "GeoLite2-City.mmdb")
IP_API_BATCH_URL = "http://ip-api.com/batch"
MAX_WORKERS      = 10
RATE_LIMIT_SLEEP = 0.06   # ~16 req/s (ip-api free limit: 45/min)

# ── California city domains ──────────────────────────────────────────────────
CALIFORNIA_CITIES = [
    "hbpd.org", "huntingtonbeachca.gov", "volunteer.huntingtonbeachca.gov",
    "newportbeachca.gov", "nbpd.org", "santamonica.gov", "santamonicapd.org",
    "cityofirvine.org", "irvinepd.org", "lacity.gov", "lapdonline.org",
    "longbeach.gov", "lbpd.org", "anaheim.net", "anaheimpd.org",
    "santa-ana.org", "santaanapd.org", "cityofgarden-grove.org",
    "ci.costa-mesa.ca.us", "cmpdca.gov", "cityofwestminster.us",
    "ci.buena-park.ca.us", "ci.fullerton.ca.us", "cityoftustin.org",
    "cityoforange.org", "lahabracity.com", "breaonline.com",
]


# ── Geolocation helpers ──────────────────────────────────────────────────────
def _geoip2_lookup(ip: str) -> dict:
    """Local MaxMind lookup. Returns {} if DB not available."""
    try:
        import geoip2.database  # type: ignore
        with geoip2.database.Reader(MMDB_PATH) as reader:
            r = reader.city(ip)
            return {
                "city":      r.city.name or "",
                "state":     r.subdivisions.most_specific.name or "",
                "country":   r.country.name or "",
                "latitude":  r.location.latitude,
                "longitude": r.location.longitude,
                "isp":       "",
                "source":    "maxmind",
            }
    except Exception:
        return {}


def _ipapi_batch(ips: list[str]) -> dict[str, dict]:
    """Batch REST lookup via ip-api.com (max 100 per request)."""
    try:
        import urllib.request
        payload = json.dumps([{"query": ip} for ip in ips]).encode()
        req = urllib.request.Request(
            IP_API_BATCH_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            results = json.loads(resp.read().decode())
        out = {}
        for r in results:
            if r.get("status") == "success":
                out[r["query"]] = {
                    "city":      r.get("city", ""),
                    "state":     r.get("regionName", ""),
                    "country":   r.get("country", ""),
                    "latitude":  r.get("lat"),
                    "longitude": r.get("lon"),
                    "isp":       r.get("isp", ""),
                    "source":    "ip-api",
                }
        return out
    except Exception as e:
        print(f"[WARN] ip-api batch failed: {e}")
        return {}


def geolocate_ip(ip: str) -> dict:
    """Geolocate a single IP (MaxMind → ip-api fallback)."""
    result = _geoip2_lookup(ip)
    if not result:
        batch = _ipapi_batch([ip])
        result = batch.get(ip, {})
    return result


def geolocate_batch(ips: list[str]) -> dict[str, dict]:
    """Geolocate a list of IPs efficiently."""
    results = {}
    # Try MaxMind first
    no_mmdb = []
    for ip in ips:
        r = _geoip2_lookup(ip)
        if r:
            results[ip] = r
        else:
            no_mmdb.append(ip)
    # Batch fallback for missing
    for i in range(0, len(no_mmdb), 100):
        chunk = no_mmdb[i:i + 100]
        batch = _ipapi_batch(chunk)
        results.update(batch)
        time.sleep(RATE_LIMIT_SLEEP)
    return results


# ── DNS resolution ───────────────────────────────────────────────────────────
def resolve_domain(domain: str) -> list[str]:
    """Resolve domain → list of IPs."""
    try:
        infos = socket.getaddrinfo(domain, None)
        return list({info[4][0] for info in infos})
    except socket.gaierror:
        return []


# ── BigQuery helpers ─────────────────────────────────────────────────────────
def _bq_client():
    try:
        from google.cloud import bigquery  # type: ignore
        return bigquery.Client(project=PROJECT_ID)
    except ImportError:
        print("[WARN] google-cloud-bigquery not installed. Skipping BQ write.")
        return None


def _ensure_tables(client) -> None:
    from google.cloud import bigquery  # type: ignore

    geo_schema = [
        bigquery.SchemaField("domain",       "STRING"),
        bigquery.SchemaField("ip",           "STRING"),
        bigquery.SchemaField("city",         "STRING"),
        bigquery.SchemaField("state",        "STRING"),
        bigquery.SchemaField("country",      "STRING"),
        bigquery.SchemaField("latitude",     "FLOAT"),
        bigquery.SchemaField("longitude",    "FLOAT"),
        bigquery.SchemaField("isp",          "STRING"),
        bigquery.SchemaField("source",       "STRING"),
        bigquery.SchemaField("record_type",  "STRING"),
        bigquery.SchemaField("status_code",  "INTEGER"),
        bigquery.SchemaField("is_exposed",   "BOOLEAN"),
        bigquery.SchemaField("scanned_at",   "TIMESTAMP"),
    ]
    for table_id, schema in [(BQ_TABLE_GEO, geo_schema)]:
        try:
            table = bigquery.Table(table_id, schema=schema)
            client.create_table(table, exists_ok=True)
        except Exception as e:
            print(f"[WARN] Could not ensure table {table_id}: {e}")


def write_to_bq(records: list[dict]) -> None:
    """Insert geolocated records into BigQuery."""
    client = _bq_client()
    if not client or not records:
        return
    _ensure_tables(client)
    errors = client.insert_rows_json(BQ_TABLE_GEO, records)
    if errors:
        print(f"[WARN] BQ insert errors: {errors[:3]}")
    else:
        print(f"[OK]   Inserted {len(records)} rows → {BQ_TABLE_GEO}")


# ── Main entry points ────────────────────────────────────────────────────────
def run_ip_lookup(ips: list[str], domain: str = "") -> list[dict]:
    """Geolocate IPs and return enriched records."""
    geo = geolocate_batch(ips)
    records = []
    ts = datetime.now(timezone.utc).isoformat()
    for ip in ips:
        g = geo.get(ip, {})
        record = {
            "domain":      domain,
            "ip":          ip,
            "city":        g.get("city", ""),
            "state":       g.get("state", ""),
            "country":     g.get("country", ""),
            "latitude":    g.get("latitude"),
            "longitude":   g.get("longitude"),
            "isp":         g.get("isp", ""),
            "source":      g.get("source", "unknown"),
            "record_type": "A",
            "status_code": 0,
            "is_exposed":  False,
            "scanned_at":  ts,
        }
        records.append(record)
        lat = g.get("latitude", "?")
        lon = g.get("longitude", "?")
        print(f"  {ip:>18}  →  {g.get('city','?')}, {g.get('state','?')}  ({lat}, {lon})  [{g.get('source','?')}]")
    return records


def scan_domains(domains: list[str]) -> list[dict]:
    """Resolve domains → IPs → geolocate."""
    all_records = []
    for domain in domains:
        print(f"\n[SCAN] {domain}")
        ips = resolve_domain(domain)
        if not ips:
            print(f"  [SKIP] No IPs resolved for {domain}")
            continue
        print(f"  Resolved: {', '.join(ips)}")
        records = run_ip_lookup(ips, domain=domain)
        all_records.extend(records)
    return all_records


def main():
    parser = argparse.ArgumentParser(
        description="City IP Geolocation v2 — MaxMind + ip-api fallback"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--ips",  nargs="+", metavar="IP",     help="Single or multiple IPs to geolocate")
    group.add_argument("--file", metavar="FILE",              help="File with one IP per line")
    group.add_argument("--city", metavar="CITY",              help="Query BQ for a specific city")
    group.add_argument("--scan-california-cities", action="store_true", help="Scan all pre-loaded CA city domains")
    group.add_argument("--domains", nargs="+", metavar="DOM", help="Custom list of domains to resolve + geolocate")

    parser.add_argument("--no-bq", action="store_true",   help="Skip BigQuery write")
    parser.add_argument("--json",  metavar="FILE",         help="Write output to JSON file")
    args = parser.parse_args()

    records: list[dict] = []

    if args.ips:
        records = run_ip_lookup(args.ips)

    elif args.file:
        with open(args.file) as f:
            ips = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        records = run_ip_lookup(ips)

    elif args.city:
        client = _bq_client()
        if not client:
            print("[ERROR] BigQuery not available for --city query.")
            sys.exit(1)
        q = f"SELECT * FROM `{BQ_TABLE_GEO}` WHERE LOWER(city) = LOWER('{args.city}') LIMIT 500"
        rows = list(client.query(q).result())
        records = [dict(r) for r in rows]
        print(f"[OK] Found {len(records)} records for city={args.city!r}")

    elif args.scan_california_cities:
        records = scan_domains(CALIFORNIA_CITIES)

    elif args.domains:
        records = scan_domains(args.domains)

    # Write to BQ
    if records and not args.no_bq:
        write_to_bq(records)

    # Write to JSON
    if args.json and records:
        with open(args.json, "w") as f:
            json.dump(records, f, indent=2, default=str)
        print(f"[OK] JSON written → {args.json}")

    print(f"\n[DONE] {len(records)} records processed.")


if __name__ == "__main__":
    main()
