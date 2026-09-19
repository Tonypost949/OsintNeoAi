# OSINTNEOAI Architecture Documentation

## Overview
Reorganized 4-tier modular application architecture dividing user-facing, admin, workspace, and developer engine layers.

```
OsintNeoAi/
├── app.py                    # Flask entry point
├── osintneoai/               # Python package
│   └── blueprints/
│       ├── main.py           # / → public landing
│       ├── admin.py          # /admin → dashboard, grid
│       ├── workspace.py      # /workspace → chat, maps, terminal
│       └── api.py            # /api → tasks, CLI exec
├── public/                   # 5 landing pages
├── admin/                    # 4 admin dashboards
├── workspace/                # 50+ user-facing HTML
├── dev/                      # 300+ engines, scripts, tests
│   ├── engines/
│   ├── scripts/
│   └── tests/
├── ARCHITECTURE.md           # Full documentation
└── ROLLBACK_PLAN.md          # Emergency procedures
```

## Blueprints Breakdown
1. **`main.py` (`/`):** Public landing page & initial blank user chat input signup.
2. **`admin.py` (`/admin`):** Master admin dashboard, capabilities grid, and task ledger.
3. **`workspace.py` (`/workspace`):** Interactive AI chat, 3D WebGL tactical maps, terminal console.
4. **`api.py` (`/api`):** REST API endpoints for autonomous task execution, CLI runners, and BigQuery data queries.
