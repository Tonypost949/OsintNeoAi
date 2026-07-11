# OSINT Independent Platform

> **⚠️ MANDATORY AGENT PROTOCOL - READ BEFORE ANY ACTION ⚠️**

**EVERY AGENT MUST:**
1. **READ THE ENTIRE REPO FIRST** - Every file, every doc, every script before touching anything
2. **FOLLOW BACKUP PROTOCOL** - All changes backed up to Google Drive `sharedall` + local C:\ BEFORE any modification
3. **NO PIGGYBACKING** - Create independent editions, don't modify existing code in place
4. **DOCUMENT EVERYTHING** - Update DISASTER_RECOVERY.md with every change

---

**Backup Locations (Tiered Redundancy):**
| Tier | Location | Purpose |
|------|----------|---------|
| 1 | GitHub `Tonypost949/OsintNeoAi` | Primary repo |
| 2 | Google Drive `sharedall/osint-indep-backup/` | Live mirror (all sizes) |
| 3 | Local `C:\osint-indep-backup\` | Hourly snapshots |
| 4 | Cold storage | Monthly bundles |

**Pre-Commit Requirement:** `./scripts/verify-backups.sh` must pass before ANY commit.

**Resurrection Test:** Monthly full restore from Tier 2 to clean machine documented in `DISASTER_RECOVERY.md`.

---

A standalone, self-contained OSINT (Open Source Intelligence) platform built from scratch. No dependencies on existing codebases. Fully maintainable by the operator.

## Architecture

```
osint-indep/
├── src/                    # Core Python application
│   ├── __init__.py
│   ├── core/              # Core modules
│   │   ├── __init__.py
│   │   ├── config.py      # Configuration management
│   │   ├── database.py    # SQLite/PostgreSQL abstraction
│   │   ├── logging.py     # Structured logging
│   │   └── security.py    # Encryption, API key management
│   ├── collectors/        # Data collection modules
│   │   ├── __init__.py
│   │   ├── base.py        # Base collector class
│   │   ├── web.py         # Web scraping
│   │   ├── api.py         # API integrations
│   │   ├── dns.py         # DNS intelligence
│   │   ├── whois.py       # WHOIS lookups
│   │   ├── cert.py        # Certificate transparency
│   │   ├── social.py      # Social media
│   │   ├── breach.py      # Breach databases
│   │   └── geo.py         # Geospatial intelligence
│   ├── analyzers/         # Analysis modules
│   │   ├── __init__.py
│   │   ├── correlation.py # Entity correlation
│   │   ├── graph.py       # Network graph analysis
│   │   ├── timeline.py    # Temporal analysis
│   │   ├── threat.py      # Threat scoring
│   │   └── pattern.py     # Pattern detection
│   ├── enrichers/         # Data enrichment
│   │   ├── __init__.py
│   │   ├── ip.py          # IP enrichment
│   │   ├── domain.py      # Domain enrichment
│   │   ├── email.py       # Email enrichment
│   │   ├── phone.py       # Phone enrichment
│   │   └── crypto.py      # Cryptocurrency addresses
│   ├── storage/           # Storage backends
│   │   ├── __init__.py
│   │   ├── sqlite.py      # SQLite backend
│   │   ├── postgres.py    # PostgreSQL backend
│   │   ├── elasticsearch.py # Elasticsearch backend
│   │   └── files.py       # File-based storage
│   └── api/               # REST API
│       ├── __init__.py
│       ├── routes.py      # API routes
│       ├── models.py      # Pydantic models
│       └── auth.py        # Authentication
├── web/                   # Web interface
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   └── templates/
├── data/                  # Data files
├── config/                # Configuration
│   ├── default.yaml
│   ├── production.yaml
│   └── development.yaml
├── scripts/               # Utility scripts
├── tests/                 # Test suite
├── docs/                  # Documentation
├── requirements.txt       # Python dependencies
├── Dockerfile             # Container build
├── docker-compose.yml     # Multi-container setup
├── Makefile              # Build automation
└── pyproject.toml        # Project metadata
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python -m src.core.database init

# Start development server
python -m src.api.routes

# Or with Docker
docker-compose up -d
```

## Configuration

Copy `config/default.yaml` to `config/local.yaml` and customize:

```yaml
database:
  type: sqlite
  path: data/osint.db

collectors:
  web:
    timeout: 30
    user_agent: "OSINT-Independent/1.0"
  api:
    shodan_key: ""
    virustotal_key: ""
    censys_id: ""
    censys_secret: ""

api:
  host: 0.0.0.0
  port: 8080
  workers: 4
```

## Features

- **Modular Collectors**: Web, API, DNS, WHOIS, Certificate Transparency, Social Media, Breach Data, Geospatial
- **Analysis Engine**: Correlation, Graph Analysis, Timeline, Threat Scoring, Pattern Detection
- **Enrichment Pipeline**: IP, Domain, Email, Phone, Cryptocurrency
- **Multiple Storage Backends**: SQLite, PostgreSQL, Elasticsearch, Files
- **REST API**: FastAPI-based with authentication
- **Web UI**: Modern interface for investigations
- **Docker Support**: Production-ready containerization
- **Security**: API key encryption, audit logging, rate limiting

## Development

```bash
# Run tests
pytest tests/

# Format code
black src/
isort src/

# Type checking
mypy src/

# Build docs
mkdocs build
```

## License

MIT - See LICENSE file