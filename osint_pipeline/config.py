"""
config.py — Central configuration for OSINT pipeline.
All secrets via env vars only. Never hardcode.
"""
import os
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────
WORKSPACE = Path(os.getenv("OSINT_WORKSPACE", r"C:\Users\HP\OSINT_WORKSPACE\NPI"))
EXPORT_DIR = WORKSPACE / "neo4j_exports"
CACHE_DIR = WORKSPACE / "cache"
LOG_DIR = WORKSPACE / "logs"

for d in [EXPORT_DIR, CACHE_DIR, LOG_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── GCP / BigQuery ─────────────────────────────────────────────
GCP_PROJECT = os.getenv("GCP_PROJECT", "project-743aab84-f9a5-4ec7-954")
BQ_DATASET = os.getenv("BQ_DATASET", "osint")
BQ_TABLE_ENTITIES = f"{GCP_PROJECT}.{BQ_DATASET}.entities"
BQ_TABLE_RELATIONSHIPS = f"{GCP_PROJECT}.{BQ_DATASET}.relationships"
BQ_TABLE_FILINGS = f"{GCP_PROJECT}.{BQ_DATASET}.filings"
BQ_TABLE_ATTORNEYS = f"{GCP_PROJECT}.{BQ_DATASET}.attorneys"
BQ_TABLE_PEOPLE = f"{GCP_PROJECT}.{BQ_DATASET}.people"
BQ_TABLE_CONTROL = f"{GCP_PROJECT}.{BQ_DATASET}.control_cluster"

# ── Neo4j ──────────────────────────────────────────────────────
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")

# ── Entity Matching ────────────────────────────────────────────
FUZZY_THRESHOLD = int(os.getenv("FUZZY_THRESHOLD", "85"))
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "300"))  # 5 min

# ── CA SOS ─────────────────────────────────────────────────────
CA_SOS_SEARCH_URL = "https://businesssearch.sos.ca.gov/DocumentSearch/Search"
CA_SOS_DETAIL_URL = "https://businesssearch.sos.ca.gov/DocumentSearch/Detail"
CA_SOS_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://businesssearch.sos.ca.gov",
    "Referer": "https://businesssearch.sos.ca.gov/",
}

# ── Pipeline ───────────────────────────────────────────────────
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "300"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "100"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
