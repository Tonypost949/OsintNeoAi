# OSINT Consolidation Tasks

- `[x]` Create target directories (`core/`, `cli/`, `database/`, `pipelines/`, `archive/`)
- `[x]` Consolidate backend files to `core/`
    - `[x]` Connectors: `ai_connector.py`, `vision_osint_connector.py`
    - `[x]` Graph builders: `ag2_rico_graph.py`, `generate_maltego.py`
    - `[x]` Analysis engines: `weaver_audit_analysis.md`, `analyze_rico_full.py`
- `[x]` Consolidate CLI files to `cli/`
    - `[x]` Move root-level CLI files
- `[x]` Consolidate Database queries & DDLs to `database/`
    - `[x]` Move SQL files (`address_cluster_monitor.sql`, etc.)
- `[x]` Consolidate pipelines to `pipelines/`
    - `[x]` Ingestion loaders
    - `[x]` Backup scripts
- `[x]` Move legacy zip extractions into `archive/`
- `[x]` Run validation test scripts to verify BQ and imports remain functional
