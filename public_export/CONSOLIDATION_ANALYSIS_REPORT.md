# OSINTNeoAi Repository Consolidation Analysis
Generated: 2026-10-19 00:38:06 UTC

## Executive Summary
Analyzed 8 related repositories against the main OsintNeoAi repository (12,712 files).
Found **790 unique files** across 7 repositories that are NOT already in the main repository.

## Repository Breakdown

| Repository | Total Files | Unique Files | Overlap % | Priority |
|------------|-------------|--------------|-----------|----------|
| osint-agent | 526 | 512 | 2.7% | CRITICAL - Core forensic dossiers, RICO investigations, 200+ analysis scripts |
| OSINTRnDi | 149 | 69 | 53.7% | HIGH - Master dossiers, evidence matrices, ArcGIS tools, BigQuery ingestion |
| osint_analyzer | 143 | 140 | 2.1% | MEDIUM - Full React/TypeScript app with entity extraction, network viz, Google Drive |
| OSINTNeoAiCLI | 40 | 36 | 10.0% | MEDIUM - Entity extraction, graph DB, IP-to-port, web search transforms |
| OSINTNeoAiXL | 16 | 12 | 25.0% | LOW - Investigation findings, SQL extraction scripts |
| osintneoai-a1 | 487 | 1 | 99.8% | IGNORE - Almost entirely duplicated (build artifacts, gradle cache, browser session) |
| OsintNeoAi52026 | 26 | 20 | 23.1% | LOW - UI components for maps, graphs, Google Workspace integration |

## Top Priority Items for Consolidation

### osint-agent (512 unique files) - CRITICAL
**Forensic Dossiers (20+ files):**
- CANONICAL_BRIEFING.md, CANONICAL_BRIEFING_MERCY_HOUSE.md
- NATIONWIDE_FOOTPRINT.md, NATIONWIDE_INDIVIDUAL_TARGETS.csv
- Dossier/Andrew_Do_Corruption_Network.md
- Dossier/RICO_Operation_Gangstas_Paradise.md
- Dossier/Huntington_Beach_HBNC.md
- CHILD_TRAFFICKING_CPS_LAYER.md
- ENVIRONMENTAL_RICO_PIPELINE.md
- FEDERAL_WHISTLEBLOWER_EXHIBIT.md
- EXHIBIT_MERCY_HOUSE_FORENSICS.md
- HB_OSINT_Forensic_Briefing.md

**Analysis Scripts (100+ files):**
- analyze_rico_full.py, analyze_rico_pandas_v2.py
- cross_reference_entities.py, cross_reference_ppp_optimized.py
- extract_all_names.py, extract_human_names.py, extract_json_intel.py
- nationwide_sweep.py, run_nationwide_deep_investigation.py
- generate_master_rico_matrix.py, generate_nationwide_holes.py

**Data Files (30+ CSV/JSON):**
- bq_rico_matches.csv, rico_evidence_matrix.csv
- MASTER_TARGET_NAMES.csv, geo_entity_map.csv
- ca_statewide_fraud_matrix.csv, tx_coc_matrix.csv

**Evidence Vaults:**
- ai_sync_vault/ (RICO matches, LLC matrices, cross-references)
- opencode_work/ (Andrew Do audit, forensic reports)

### OSINTRnDi (69 unique files) - HIGH
**Master Documents:**
- MASTER_OSINT_CONSOLIDATED_DOSSIER.md
- EVIDENCE_MATRIX.md
- FORENSIC_AUDIT_REPORT.md
- ARCGIS_SPATIAL_INTELLIGENCE_DOSSIER.md
- GITHUB_MASTER_EXTRACTION_VAULT.md

**Core Scripts:**
- aegis_correlation_engine.py
- bulk_load_graph_to_bq.py
- osint_network_visualizer.py
- run_nationwide_deep_investigation.py
- people-extraction-workbook.py
- onedrive_ingestion_engine.py
- ingest_photos_chunked.py

### OSINTNeoAiCLI (36 unique files) - MEDIUM
**Core Capabilities:**
- core/ai_agent.py - AI agent framework
- core/entities.py - Entity extraction
- core/graph_db.py - Graph database operations
- core/transforms.py - Transform pipeline
- transforms/IPToPorts.py - IP to port mapping
- transforms/WebSearch.py - Web search integration

### osint_analyzer (140 unique files) - MEDIUM
**Full Application Stack:**
- React/TypeScript frontend with network visualization
- Google Drive/Docs/Mail/Sheets integration
- Document entity extraction and relationship mapping
- Dashboard with analysis stats and filtering

### OSINTNeoAiXL (12 unique files) - LOW
- investigation_findings.md, osint_matrix_report.md
- SQL extraction scripts (hb_extraction_query.sql, inject_*.sql)

### OsintNeoAi52026 (20 unique files) - LOW
- React components: MapTracker, NetworkGraph, NeoAnalysis
- Google Workspace libs: googleAuth, googleDrive, googleDocs, googleMail, googleSheets

## Recommended Consolidation Plan

### Phase 1: Critical Forensic Evidence (Week 1)
Copy all osint-agent dossiers to evidence/dossiers/
Copy all osint-agent CSV/JSON evidence to evidence/data/
Copy all analysis scripts to scripts/forensic/

### Phase 2: Core Investigation Scripts (Week 1-2)
Copy OSINTRnDi correlation engine, BigQuery loaders, network visualizer
Copy osint-agent nationwide investigation scripts
Merge into scripts/investigation/

### Phase 3: Application Capabilities (Week 2-3)
Integrate OSINTNeoAiCLI entity/graph/transform modules into src/core/
Evaluate osint_analyzer React components for adoption
Integrate OsintNeoAi52026 Google Workspace libs

### Phase 4: Reference Materials (Week 3)
Archive OSINTNeoAiXL SQL scripts to scripts/sql/archive/
Document any unique findings from investigation_findings.md

## Files to IGNORE
- osintneoai-a1: 486/487 files are build artifacts, gradle cache, Playwright browser session
- Only unique file: .github/workflows/pages.yml (likely already covered)

## Evidence Locker Targets
Per OVERRIDE OPTIONS, consolidate to:
- Primary: C:\Amd949609_Antigravity_v1\evidence\
- Cloud mirror: C:\Amd949609_Antigravity_v1\cloud_storage\evidence_locker\
- Google Drive: C:\Amd949609_Antigravity_v1\cloud_storage\gdrive_backup\

## Next Steps
1. Review CSV at C:\OsintNeoAi\repo_consolidation_analysis.csv (790 rows)
2. Execute Phase 1 copy operations
3. Run deduplication check against Evidence Locker Master Index
4. Update Master Index with new entries

