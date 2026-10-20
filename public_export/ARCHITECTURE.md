# OSINT Neo AI — Architecture

## Overview

OSINT Neo AI is a decentralized, hybrid-cloud open-source intelligence platform. This document describes the project structure, Flask application architecture, and deployment topology.

## Directory Structure

```
OsintNeoAi/
├── app.py                      # Flask application entry point
├── osintneoai/                 # Python package (Flask blueprints)
│   ├── __init__.py
│   └── blueprints/
│       ├── __init__.py
│       ├── main.py             # Main/public routes
│       ├── admin.py            # Admin backend routes
│       ├── workspace.py        # User workspace routes
│       └── api.py              # REST API routes
├── public/                     # Public landing pages
│   ├── index.html
│   ├── hbnc_rico_gis.html
│   ├── badass_osint_map.html
│   ├── PUBLIC_RECON_AUDIT.html
│   └── workspace_chat.html
├── admin/                      # Admin backend
│   ├── dashboard.html
│   ├── master_admin_dashboard.html
│   ├── capabilities_dashboard.html
│   └── task_system_dashboard.html
├── workspace/                  # User workspace
│   ├── gemini_chat.html
│   ├── terminal.html
│   ├── maps_hub.html
│   ├── victims_board.html
│   ├── tasks.html
│   ├── gods_eye_view.html
│   ├── maplibre_3d_tactical.html
│   ├── newspaper_hub.html
│   ├── whistleblower_legal_index.html
│   ├── omnichannel_legal_hub.html
│   ├── legal_conflict_audit_dossier.html
│   └── ... (50+ HTML files)
├── dev/                        # Developer environment
│   ├── engines/               # Core Python engines
│   │   ├── spark_intelligence_engine.py
│   │   ├── autonomous_daily_compiler.py
│   │   ├── aegis_correlation_engine.py
│   │   └── ... (100+ engines)
│   ├── scripts/               # Utility scripts
│   │   ├── install_cli_tools.sh
│   │   ├── deploy_azure.ps1
│   │   └── ... (200+ scripts)
│   └── tests/                 # Test files
│       ├── test_all_links_live.py
│       ├── test_maps_open_live.py
│       └── ...
├── reports/                    # Generated reports
│   └── spark_digests/
├── research/                   # Research papers
│   └── arxiv_papers/
├── tools/                      # MCP tools
│   └── openosint_mcp_server.py
├── .github/workflows/          # CI/CD
│   └── spark_intelligence_engine.yml
├── .env                        # Environment variables (gitignored)
├── .env.example                # Environment template
├── requirements.txt            # Python dependencies
├── ARCHITECTURE.md             # This file
└── ROLLBACK_PLAN.md            # Deployment rollback plan
```

## Flask Application Architecture

### Entry Point

`app.py` creates the Flask application and registers blueprints:

```python
from flask import Flask
from osintneoai.blueprints import main_bp, admin_bp, workspace_bp, api_bp

def create_app():
    app = Flask(__name__, static_folder='.')
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(workspace_bp)
    app.register_blueprint(api_bp)
    return app
```

### Blueprints

| Blueprint | Prefix | Purpose |
|-----------|--------|---------|
| `main_bp` | `/` | Public landing, manifest, health check |
| `admin_bp` | `/admin` | Admin dashboard, capabilities, grid |
| `workspace_bp` | `/workspace` | User chat, maps, terminal, victims |
| `api_bp` | `/api` | REST API (status, auth, tasks, CLI) |

### Route Map

| Route | Blueprint | File | Description |
|-------|-----------|------|-------------|
| `/` | main | `public/index.html` | Landing page |
| `/signup` | main | `public/workspace_chat.html` | User signup |
| `/landing` | main | `public/index.html` | Landing page alias |
| `/admin` | admin | `admin/dashboard.html` | Admin dashboard |
| `/workspace` | workspace | `public/workspace_chat.html` | User workspace |
| `/chat` | workspace | `public/workspace_chat.html` | AI chat |
| `/dev` | workspace | `web/index.html` | Developer workspace |
| `/legal` | workspace | `workspace/whistleblower_legal_index.html` | Legal portal |
| `/legal/omnichannel` | workspace | `workspace/omnichannel_legal_hub.html` | Omnichannel legal |
| `/legal/conflicts` | workspace | `workspace/legal_conflict_audit_dossier.html` | Legal conflicts |
| `/api/status` | api | - | Health check |
| `/api/auth/register` | api | - | User registration |
| `/api/auth/session` | api | - | Session info |

## Layers

### 1. Public Layer (`/public/`)
- Landing pages and marketing content
- No authentication required
- Static HTML served directly

### 2. Admin Layer (`/admin/`)
- Dashboard and system management
- Task oversight and capabilities monitoring
- Data grid with filtering/export

### 3. Workspace Layer (`/workspace/`)
- User-facing tools and interfaces
- AI chat (Gemini integration)
- Maps (Google Maps, MapLibre 3D)
- Terminal (CLI access)
- Evidence boards and FOIA tracking

### 4. Developer Layer (`/dev/`)
- Python engines for data processing
- Scripts for automation and deployment
- Test files for validation

### 5. API Layer (`/api/`)
- REST endpoints for frontend consumption
- User authentication and session management
- CLI execution proxy

## Key Components

### Spark Intelligence Engine
- Location: `dev/engines/spark_intelligence_engine.py`
- Function: Daily OSINT digest generation via Gemini AI
- Schedule: GitHub Actions cron at 13:00 UTC
- Output: Email digest + CSV correlations

### MCP Server
- Location: `tools/openosint_mcp_server.py`
- Function: 19 native OSINT tools for AI assistants
- Integration: Antigravity CLI, Claude Code, Gemini CLI

### BigQuery Ledger
- Project: `noble-beanbag-497411-m4`
- Function: Append-only forensic evidence storage
- Auth: Workload Identity Federation

### Web3 Contracts (Sepolia)
- StakingGate: `0xdA7655b7007a1C7F8191066Bb9A69E4D8987E725`
- MultiPoolEscrow: `0x15564C9A8a5903336CC67F2cBa00dBdAd944dC5B`
- USDC: `0x7236F4982a31537d07f3182A1CdAD3f3E4452A53`
- OSINT: `0xA74B3fAfd838fC273f7c6e201B6210AC2b3A0296`

## Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `GEMINI_API_KEY` | Google Gemini API | Yes |
| `GOOGLE_MAPS_API_KEY` | Maps/Geocoding | Yes |
| `SMTP_USER` | Email sender | Yes |
| `SMTP_PASSWORD` | Email auth | Yes |
| `ALERT_RECIPIENT_EMAIL` | Digest recipient | Yes |
| `GITHUB_PAT` | GitHub API access | Yes |
| `GCP_PROJECT_ID` | GCP project | No |
| `LIGHTBOX_API_KEY` | Lightbox integration | No |

## Deployment

### Local Development
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### GitHub Actions
- Workflow: `.github/workflows/spark_intelligence_engine.yml`
- Schedule: Daily at 13:00 UTC
- Secrets: Stored in GitHub repository settings

### Rollback
See `ROLLBACK_PLAN.md` for emergency procedures.
