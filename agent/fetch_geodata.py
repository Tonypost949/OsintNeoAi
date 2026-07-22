"""
fetch_geodata.py
================
Pulls geolocated city IP data from BigQuery and writes a JSON marker cache
for the CityCyberReconMap React dashboard.

Usage:
    python fetch_geodata.py [--output path/to/output.json]

BigQuery source:
    project-743aab84-f9a5-4ec7-954.national_audits.ip_geolocation_index

Output (default):
    web/client/src/data/cyber_recon_geo.json
"""

import json
import os
import argparse
import sys
from datetime import datetime, timezone

# ── BigQuery setup ──────────────────────────────────────────────────────────
PROJECT_ID = "project-743aab84-f9a5-4ec7-954"
BQ_TABLE   = f"{PROJECT_ID}.national_audits.ip_geolocation_index"

# Default output path (relative to repo root)
DEFAULT_OUTPUT = os.path.join(
    os.path.dirname(__file__),
    "..", "web", "client", "src", "data", "cyber_recon_geo.json"
)


def fetch_from_bigquery(output_path: str) -> None:
    """Query BigQuery and write marker JSON."""
    try:
        from google.cloud import bigquery  # type: ignore
    except ImportError:
        print("[ERROR] google-cloud-bigquery not installed.")
        print("        Run:  pip install google-cloud-bigquery")
        sys.exit(1)

    client = bigquery.Client(project=PROJECT_ID)

    query = f"""
        SELECT
            domain,
            ip,
            city,
            state,
            country,
            latitude,
            longitude,
            status_code,
            is_exposed,
            isp,
            record_type
        FROM `{BQ_TABLE}`
        WHERE
            latitude  IS NOT NULL
            AND longitude IS NOT NULL
            AND latitude  BETWEEN -90  AND 90
            AND longitude BETWEEN -180 AND 180
        ORDER BY is_exposed DESC, domain
    """

    print(f"[INFO] Querying {BQ_TABLE}...")
    rows = list(client.query(query).result())
    print(f"[INFO] Got {len(rows)} rows.")

    locations = []
    for row in rows:
        locations.append({
            "domain":      row.get("domain", ""),
            "ip":          row.get("ip", ""),
            "city":        row.get("city", ""),
            "state":       row.get("state", ""),
            "country":     row.get("country", ""),
            "lat":         float(row.get("latitude", 0)),
            "lng":         float(row.get("longitude", 0)),
            "status_code": row.get("status_code", 0),
            "is_exposed":  bool(row.get("is_exposed", False)),
            "isp":         row.get("isp", ""),
            "record_type": row.get("record_type", "A"),
        })

    _write_output(locations, output_path)


def fetch_fallback_demo(output_path: str) -> None:
    """Write a static demo payload when BigQuery is unavailable."""
    print("[WARN] Using built-in demo data (no BigQuery credentials found).")
    demo = [
        {"domain": "hbpd.org",              "ip": "162.242.210.88", "city": "Huntington Beach", "state": "CA", "country": "US", "lat": 33.6595, "lng": -117.9988, "status_code": 200, "is_exposed": True,  "isp": "OC Public Fiber",         "record_type": "A"},
        {"domain": "huntingtonbeachca.gov",  "ip": "162.242.210.89", "city": "Huntington Beach", "state": "CA", "country": "US", "lat": 33.6600, "lng": -117.9990, "status_code": 200, "is_exposed": False, "isp": "OC Public Fiber",         "record_type": "A"},
        {"domain": "santamonicapd.org",      "ip": "23.21.198.44",   "city": "Santa Monica",     "state": "CA", "country": "US", "lat": 34.0195, "lng": -118.4912, "status_code": 200, "is_exposed": True,  "isp": "Westside Muni Cloud",     "record_type": "A"},
        {"domain": "santamonica.gov",        "ip": "23.21.198.45",   "city": "Santa Monica",     "state": "CA", "country": "US", "lat": 34.0196, "lng": -118.4914, "status_code": 301, "is_exposed": False, "isp": "Westside Muni Cloud",     "record_type": "A"},
        {"domain": "cityofirvine.org",       "ip": "192.195.82.101", "city": "Irvine",           "state": "CA", "country": "US", "lat": 33.6846, "lng": -117.8265, "status_code": 200, "is_exposed": False, "isp": "Irvine Spectrum Net",     "record_type": "A"},
        {"domain": "irvinepd.org",           "ip": "192.195.82.102", "city": "Irvine",           "state": "CA", "country": "US", "lat": 33.6847, "lng": -117.8266, "status_code": 200, "is_exposed": False, "isp": "Irvine Spectrum Net",     "record_type": "A"},
        {"domain": "lapdonline.org",         "ip": "141.218.2.10",   "city": "Los Angeles",      "state": "CA", "country": "US", "lat": 34.0522, "lng": -118.2437, "status_code": 200, "is_exposed": True,  "isp": "LA City Fiber backbone",  "record_type": "A"},
        {"domain": "santaanapd.org",         "ip": "198.143.44.12",  "city": "Santa Ana",        "state": "CA", "country": "US", "lat": 33.7455, "lng": -117.8677, "status_code": 200, "is_exposed": True,  "isp": "Southern CA Municipal Net","record_type": "A"},
        {"domain": "dallaspolice.net",       "ip": "209.124.180.12", "city": "Dallas",           "state": "TX", "country": "US", "lat": 32.7767, "lng": -96.7970,  "status_code": 200, "is_exposed": True,  "isp": "Texas Public Cyber Infra", "record_type": "A"},
        {"domain": "newportbeachca.gov",     "ip": "64.145.82.10",   "city": "Newport Beach",    "state": "CA", "country": "US", "lat": 33.6189, "lng": -117.9289, "status_code": 200, "is_exposed": False, "isp": "OC City Net",             "record_type": "A"},
    ]
    _write_output(demo, output_path)


def _write_output(locations: list, output_path: str) -> None:
    """Write marker JSON with metadata envelope."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_table":  BQ_TABLE,
        "total":         len(locations),
        "exposed_count": sum(1 for m in locations if m.get("is_exposed")),
        "markers":       locations,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"[OK]   Wrote {len(locations)} markers -> {output_path}")
    print(f"       Exposed: {payload['exposed_count']}")


def main():
    parser = argparse.ArgumentParser(description="Fetch BigQuery geo markers for CityCyberReconMap.")
    parser.add_argument("--output", default=DEFAULT_OUTPUT,
                        help=f"Output JSON path (default: {DEFAULT_OUTPUT})")
    parser.add_argument("--demo", action="store_true",
                        help="Use built-in demo data instead of BigQuery")
    args = parser.parse_args()

    output = os.path.abspath(args.output)
    print(f"[INFO] Output: {output}")

    if args.demo:
        fetch_fallback_demo(output)
        return

    try:
        fetch_from_bigquery(output)
    except Exception as e:
        print(f"[WARN] BigQuery failed ({e}). Falling back to demo data.")
        fetch_fallback_demo(output)


if __name__ == "__main__":
    main()
