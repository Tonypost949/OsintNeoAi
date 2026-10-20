# Implementation Plan: OSINT Repository Consolidation

This plan proposes the structural consolidation of your various local and GitHub OSINT project folders into a single, unified codebase under the **OsintNeoAi** repository.

## Goal

To combine the best parts of the distinct OSINT repositories on your PC (`OSINTNeoAI-Core`, `OSINTNeoAiCLI`, `OSINTNeoAiXL`, `OsintNeoAi52026`, `OsintNeoAiXXXL`, `osint-agent`, `osint_analyzer`, `riconow`, etc.) into a cohesive, organized, and production-ready workspace structure without losing critical scripts or data.

---

## Proposed Project Architecture

We will organize the root directory `c:\Users\HP\OneDrive\Documents\OsintNeoAi` into the following structured components:

```
OsintNeoAi/
├── core/                  # Unified backend logic, AI connectors, & analysis engines
│   ├── connectors/        # ProPublica, GeoTracker, Google Drive/Gmail integrations
│   ├── graph/             # Network graph generation (ag2_rico_graph, Neo4j builders)
│   └── analysis/          # Forensic engines (weaver_audit, anomaly_alerts)
├── cli/                   # Standardized Command Line Interface entry points
├── web/                   # Primary React + Vite dashboard frontend
├── database/              # BigQuery schema definitions (DDL) and SQL queries
└── pipelines/             # Ingestion, backup, and automation scripts
```

---

## Proposed Changes & Consolidation Flow

### 1. Backend Integration (under [core](file:///c:/Users/HP/OneDrive/Documents/OsintNeoAi/core))
- **Consolidate AI Connectors**: Move root-level and core AI logic (`ai_connector.py`, `vision_osint_connector.py`) to `core/connectors/`.
- **Consolidate Graph Generation**: Move graph scripts (`ag2_rico_graph.py`, `generate_maltego.py`, `trace_remittance_network.py`) to `core/graph/`.
- **Consolidate Forensic Analytics**: Move specialized analyzers (`weaver_audit_analysis.md`, `analyze_rico_full.py`, `analyze_regional_holes.py`) into `core/analysis/`.

### 2. Command Line Interface (under [cli](file:///c:/Users/HP/OneDrive/Documents/OsintNeoAi/cli))
- Merge CLI wrappers and interfaces from `OSINTNeoAiCLI` and root-level scripts (`run_user_query.py`, `query_agents.py`) into the `cli/` module.

### 3. Database & Pipelines (under [database](file:///c:/Users/HP/OneDrive/Documents/OsintNeoAi/database) and [pipelines](file:///c:/Users/HP/OneDrive/Documents/OsintNeoAi/pipelines))
- **Move DDLs**: Move all DDL and SQL query scripts (`address_cluster_monitor.sql`, `cross_jurisdiction_funnel.sql`, `forensic_cross_join.sql`) into a dedicated `database/queries/` directory.
- **Move Ingestion Pipelines**: Move loaders (`ingest_photos_bq.py`, `ingest_public_records.py`, `load_convergence_data.py`, `load_forensic_layers.py`) into `pipelines/ingestion/`.
- **Move Backup Utilities**: Move sync/backup scripts (`sync_git_to_drive.py`, `backup_scratch_zips.py`) into `pipelines/backups/`.

### 4. Archive & Cleanup (under a new [archive/](file:///c:/Users/HP/OneDrive/Documents/OsintNeoAi/archive) directory)
- Move raw zip-extract folders (`OSINTNeoAiXL`, `OsintNeoAiXXXL`, etc.) into an `archive/` folder to clean up the workspace root while preserving the original historical references.

---

## Open Questions for User Feedback

> [!IMPORTANT]
> 1. **Drizzle / Node Backend**: Do you want to preserve the Express/Drizzle backend from `osint_analyzer` as part of the primary `web/` API, or keep the existing `agent/app.py` Flask backend as the main API layer?
> 2. **Verification & Testing**: Which main pipeline script (e.g., `osint_workbook_engine.py` or `ag2_rico_graph.py`) would you like to run as the primary validation test after restructure?

---

## Verification Plan

### Automated Verification
- Run python syntax tests on the reorganized directories.
- Run `list_bq_tables.py` and `verify_dossier.py` from their new paths to verify BigQuery connectivity remains intact.

### Manual Verification
- Verify the local React server in `web/` launches correctly.
- Verify the Flask dashboard (`agent/app.py`) loads modules successfully.
