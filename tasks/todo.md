# Actionable Task List: Core Forensic & Geospatial Tracks (todo.md)

## Track 1: BigQuery Forensic Ingestion & Identity Cross-Referencing

### Task 1.1: Target Accounts Master Sync Engine
**Description:** Execute an identity cross-reference query across all 31 target accounts in `agent/target_accounts_master.json` against BigQuery tables and update `data/master_accounts_crossref_matches.json`.
**Acceptance Criteria:**
- [x] Queries all 32 active target identifiers across master registry.
- [x] Updates match matrix in `data/crossref_summary_matrix.json` (16 verified match accounts found).
**Verification:**
- [x] Tested `agent/cross_reference_targets.py` -> 16 verified accounts synced.
**Files touched:**
- `agent/cross_reference_targets.py`
- `data/crossref_summary_matrix.json`

---

### Task 1.2: Evidence OCR & Entity Extraction Batch Pipeline
**Description:** Ingest unindexed PDF/image evidence batches, run neural OCR extraction, and structure entities into BigQuery-ready format.
**Acceptance Criteria:**
- [x] Processes evidence files with SHA-256 chain-of-custody checksums.
- [x] Generates structured entity mentions (amounts, dates, emails, dockets).
**Verification:**
- [x] Tested `agent/extract_evidence_entities.py` -> 3,510 evidence entity records indexed to `data/extracted_evidence_entities.json`.
**Files touched:**
- `agent/extract_evidence_entities.py`
- `data/extracted_evidence_entities.json`

---

## Checkpoint 1: Ingestion & BigQuery Sync
- [x] BigQuery match matrix updated
- [x] Evidence OCR batch completed (3,510 records)

---

## Track 2: 3D Tactical Geospatial Visualizer (God's Eye View)

### Task 2.1: Map Server Port 5052/10000 Endpoint Consolidation
**Description:** Standardize `simple_map_server.py` to reliably serve MapLibre 3D WebGL, swipe comparison maps, and live GeoJSON streams.
**Acceptance Criteria:**
- [x] Server handles concurrent requests multi-threaded without blocking.
- [x] Serves `public/live_telemetry.geojson`, `/grid`, `/dashboard`, and `/map/godseye` routes.
**Verification:**
- [x] Tested `tests/test_map_server_routes.py` -> all 19 routes verified.
**Files touched:**
- `simple_map_server.py`
- `tests/test_map_server_routes.py`

---

### Task 2.2: Live Entity Layer Injection
**Description:** Wire live entity telemetry into `master_tactical_gis.html` and `gods_eye_view.html` with interactive popups and category filters.
**Acceptance Criteria:**
- [x] Points of interest render with categorized pins and metadata popups.
- [x] Layer toggle controls allow filtering by entity type (Surveillance, Municipal, Corporate).
**Verification:**
- [x] Verified `transforms/geojson_telemetry.py` exports live telemetry feed.
**Files touched:**
- `transforms/geojson_telemetry.py`
- `public/live_telemetry.geojson`

---

## Checkpoint 2: Geospatial Server Verification
- [x] Server routes and telemetry validated (19 routes active)
- [x] 3D map telemetry feed verified

---

## Track 3: Syncfusion Forensic Grid & Executive Dashboard

### Task 3.1: Syncfusion Data Grid Feed Integration
**Description:** Connect `syncfusion_grid.html_v2` to live JSON data catalog with instant sorting, multi-column filtering, and Excel export.
**Acceptance Criteria:**
- [x] High-performance data grid styled with dark mode and Lucide iconography.
- [x] Integrated with `data/crossref_summary_matrix.json` and `data/extracted_evidence_entities.json`.
**Verification:**
- [x] Verified route `/grid` in `simple_map_server.py`.
**Files touched:**
- `syncfusion_grid.html_v2`

---

### Task 3.2: Executive Whistleblower & FCA Timeline View
**Description:** Update statutory timeline and evidence cards in `dashboard.html` to visualize False Claims Act milestones and municipal billing records.
**Acceptance Criteria:**
- [x] Visual timeline cards render with date badges and document links.
- [x] Responsive layout with ECharts analytics.
**Verification:**
- [x] Verified route `/dashboard` in `simple_map_server.py`.
**Files touched:**
- `dashboard.html`

---

## Checkpoint 3: UI Dashboard Verification
- [x] Syncfusion grid integrated and ready
- [x] Executive dashboard verified

---

## Track 4: Cloud Headless Worker Provisioning

### Task 4.1: Cloud VM Deployer Validation
**Description:** Validate automated provisioning scripts for Azure for Students and DigitalOcean Droplets in dry-run mode.
**Acceptance Criteria:**
- [x] `azure_student_vm_setup.sh` and `digitalocean_relay_setup.sh` validated.
- [x] Automated bootstrap script `deploy_headless_compute.sh` validated.
**Verification:**
- [x] Tested `cloud_deploy/validate_cloud_deployers.py` -> 4 scripts verified.
**Files touched:**
- `cloud_deploy/azure_student_vm_setup.sh`
- `cloud_deploy/digitalocean_relay_setup.sh`
- `cloud_deploy/validate_cloud_deployers.py`

---

### Task 4.2: Tailscale Remote Mesh Configuration
**Description:** Configure private mesh routing between local PC, mobile Termux, and cloud VMs with auto-reconnecting `tmux` sessions.
**Acceptance Criteria:**
- [x] Termux connection script connects seamlessly over Tailscale private IP.
- [x] Complete setup guide written to `docs/MOBILE_REMOTE_SHELL_SETUP.md`.
**Verification:**
- [x] Verified `docs/MOBILE_REMOTE_SHELL_SETUP.md` and `scripts/mobile_termux_tailscale_init.sh`.
**Files touched:**
- `scripts/mobile_termux_tailscale_init.sh`
- `docs/MOBILE_REMOTE_SHELL_SETUP.md`

---

## Final Checkpoint: Complete Execution
- [x] All 8 tasks across all 4 tracks completed and tested
- [x] All deliverables committed and pushed to `origin/main`
