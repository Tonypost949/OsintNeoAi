# Sentinel OSINT Engine - Independent Edition

---

## MANDATORY: AGENT INSTRUCTIONS

**YOU ARE AN AGENT WORKING ON THIS REPO. READ THIS ENTIRE FILE FIRST.**

**READ THESE FILES IN THIS ORDER BEFORE MAKING ANY CHANGES:**

1. `BACKUP_PROTOCOL.md` - Backup and resurrection instructions (MANDATORY)
2. `README.md` - This file (architecture, usage, backup links)
3. `CHANGELOG.md` - What has changed recently (if exists)
4. `session_summary_*.md` - Recent work sessions (if exists)

**BEFORE ANY CHANGE:**
- Run `python backup/pre_change_backup.py "description of changes"`
- Verify backups: `python backup/verify_backups.py`
- Check git status: `git status`
- Document what you are about to do

**AFTER ANY CHANGE:**
- Run tests: `python tests/test_engine.py`
- Commit: `git add -A && git commit -m "what changed" && git push`
- Backup: `python backup/sync_to_sharedall.py`
- Backup: `python backup/sync_to_local.py`
- Update session summary

**BACKUP LOCATIONS (in order of priority):**
1. GitHub: `https://github.com/Tonypost949/OsintNeoAi`
2. Local C: `C:\Users\HP\OneDrive\Documents\opencode_work\`
3. SharedAll: Google Drive shared folder (off-the-books backup)
4. Local backups: `C:\Users\HP\OneDrive\Documents\github_backups\`

**THIS SENTINEL EDITION IS INDEPENDENT. It does not depend on the rest of the OsintNeoAi repo. It can be resurrected by cloning just this directory.**

---

**A self-contained Open Source Intelligence investigation platform built from scratch.**

Created: July 10, 2026 | Version: 1.0.0 | Edition: Sentinel

---

## What This Is

Sentinel is an independent OSINT investigation engine. It does NOT depend on or piggyback on any other OSINT platform. It has its own:

- Entity extraction engine (regex-based, zero API dependency)
- Network graph analysis (BFS, centrality, community detection, bridge finding)
- Document ingestion pipeline
- Data collectors (web search, certificate transparency, WHOIS, public records)
- Risk assessment and pattern detection
- Export to HTML reports, GeoJSON maps, GEXF (Gephi), Markdown
- SQLite-backed persistent graph storage
- Full CLI interface

---

## Quick Start

```bash
cd sentinel-edition

# Install dependencies (only requests is required)
pip install -r requirements.txt

# Run tests to verify everything works
python tests/test_engine.py

# Start investigating
python cli.py investigate "target@example.com"
python cli.py ingest /path/to/documents/
python cli.py analyze
python cli.py report
python cli.py html report.html
```

---

## Architecture

```
sentinel-edition/
├── core/
│   ├── __init__.py
│   └── engine.py           # Main engine: Entity, Relationship, Graph, Extractor, Ingester, Analyzer
├── collectors/
│   ├── __init__.py
│   ├── web_collector.py    # DuckDuckGo, Wayback Machine, crt.sh, RDAP, Shodan, AbuseIPDB
│   └── public_records.py   # NPI Registry, SEC EDGAR, USASpending, PACER
├── analyzers/
│   ├── __init__.py
│   ├── text_analyzer.py    # Keyword extraction, risk assessment, financial figure detection
│   └── network_analyzer.py # Graph algorithms: centrality, bridges, communities, PageRank
├── exports/
│   ├── __init__.py
│   ├── html_report.py      # Self-contained HTML reports with search
│   └── geojson_export.py   # Geographic mapping export
├── config/
│   └── config.example.json
├── tests/
│   └── test_engine.py      # Full test suite
├── backups/                 # Independent backup storage
├── cli.py                   # Command-line interface
├── requirements.txt
└── README.md                # This file
```

---

## Core Components

### Entity Types Supported
- `person` - Individual names
- `organization` - Companies, nonprofits, agencies
- `address` - Physical locations
- `phone` - Phone numbers (US format)
- `email` - Email addresses
- `domain` - Domain names
- `ip_address` - IPv4 addresses
- `vehicle` - Vehicle identifiers
- `property` - Real estate
- `document` - Referenced documents
- `financial_account` - EINs, account numbers
- `social_profile` - Social media profiles
- `alias` - Alternative names

### Relationship Types
Any string. Examples: `works_at`, `owns`, `connected_to`, `transferred_to`, `registered_agent_for`, `co_director_with`, `same_address_as`

### Data Collectors (No API Keys Required)

| Collector | Source | What It Does |
|-----------|--------|-------------|
| `duckduckgo` | DuckDuckGo | Web search results |
| `wayback` | Internet Archive | Historical web snapshots |
| `crtsh` | crt.sh | Certificate transparency logs |
| `rdap` | RDAP.org | Domain WHOIS data |
| `nppes` | CMS.gov | Healthcare provider NPI lookup |
| `sec_edgar` | SEC.gov | Corporate filings (10-K, 10-Q, 8-K) |
| `usaspending` | USASpending.gov | Federal contract/award data |

### Data Collectors (API Keys Required)

| Collector | Source | Free Tier | Key Registration |
|-----------|--------|-----------|-----------------|
| `abuseipdb` | AbuseIPDB.com | 1000/day | https://www.abuseipdb.com/account/api |
| `shodan` | Shodan.io | Limited | https://account.shodan.io/register |
| `pacer` | PACER.gov | No ($0.10/page) | https://pacer.uscourts.gov/register |

---

## CLI Commands

```bash
# Investigation
python cli.py investigate <target>           # Start investigation on any target
python cli.py investigate john@example.com
python cli.py investigate "Acme Corporation"

# Data Ingestion
python cli.py ingest <file_or_directory>     # Extract entities from documents
python cli.py ingest ./evidence/
python cli.py ingest report.txt

# Search
python cli.py search <query>                 # Search the entity graph

# Analysis
python cli.py analyze                        # Run full network analysis
python cli.py timeline                       # Show chronological events
python cli.py stats                          # Show graph statistics

# Data Collection
python cli.py collect <source> <query>       # Run a collector
python cli.py collect duckduckgo "target company"
python cli.py collect nppes "Mercy House"
python cli.py collect crtsh "example.com"
python cli.py sources                        # List all available sources

# Export
python cli.py report [output.md]             # Markdown report
python cli.py html [output.html]             # Interactive HTML report
python cli.py geojson [output.geojson]       # Map-ready GeoJSON
python cli.py export json [output.json]      # Raw graph JSON
python cli.py export gexf [output.gexf]      # Gephi format
```

---

## Programmatic Usage

```python
from core.engine import SentinelEngine

# Initialize
engine = SentinelEngine(workspace="./my-investigation")

# Investigate
engine.investigate("target@company.com")
engine.investigate("Acme Holdings LLC")

# Ingest documents
engine.ingest("./evidence/financial_records.txt")
engine.ingest("./emails/")

# Manual entity linking
entities = engine.search("Acme")
engine.link(entities[0].id, entities[1].id, "owns", weight=0.9)

# Analyze
results = engine.analyze()
print(results["graph_stats"])
print(results["top_central_entities"])

# Export
engine.report("investigation_report.md")
engine.export_graph("gexf", "network.gexf")
```

---

## Independent Backup Links

All dependencies and data sources are independently accessible:

### Python Dependencies (PyPI)
- requests: https://pypi.org/project/requests/
- openpyxl: https://pypi.org/project/openpyxl/
- pandas: https://pypi.org/project/pandas/
- flask: https://pypi.org/project/Flask/
- networkx: https://pypi.org/project/networkx/

### Data Source Backup URLs
- NPI Registry API: https://npiregistry.cms.hhs.gov/api/
- SEC EDGAR: https://www.sec.gov/edgar/searchedgar/companysearch
- USASpending.gov API: https://api.usaspending.gov/
- DuckDuckGo Search: https://html.duckduckgo.com/html/
- Wayback Machine API: https://web.archive.org/cdx/search/cdx
- crt.sh Certificate Search: https://crt.sh/
- RDAP (WHOIS): https://rdap.org/
- AbuseIPDB: https://www.abuseipdb.com/
- Shodan: https://shodan.io/

### Documentation References
- SQLite Python: https://docs.python.org/3/library/sqlite3.html
- re (Regex): https://docs.python.org/3/library/re.html
- json: https://docs.python.org/3/library/json.html
- hashlib: https://docs.python.org/3/library/hashlib.html
- GeoJSON Spec: https://geojson.org/
- GEXF Format: https://gephi.org/gexf/
- BigQuery Public Datasets: https://cloud.google.com/bigquery/public-data

### Google Cloud Free Tier
- Cloud Run: https://cloud.google.com/run
- BigQuery (1TB/month free): https://cloud.google.com/bigquery
- Vertex AI: https://cloud.google.com/vertex-ai

### Code Backup
- GitHub Repo: https://github.com/Tonypost949/OsintNeoAi/tree/main/sentinel-edition
- This edition is self-contained. Clone the `sentinel-edition/` directory and it runs standalone.

---

## Deployment

### Local
```bash
pip install -r requirements.txt
python cli.py stats
```

### Docker
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY sentinel-edition/ .
RUN pip install -r requirements.txt
CMD ["python", "cli.py", "stats"]
```

### Google Cloud Run
```bash
gcloud run deploy sentinel-osint \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## License

This is an independent creation. Use freely.
No dependency on any prior OSINT platform code.
All algorithms are implemented from scratch using Python stdlib + requests.

---

## Backups

The `backups/` directory stores:
- Exported graph snapshots
- Report archives
- Ingested document hashes (dedup tracking)
- Configuration backups

All data is also persisted in SQLite (`investigation.db`) which is portable and self-contained.
