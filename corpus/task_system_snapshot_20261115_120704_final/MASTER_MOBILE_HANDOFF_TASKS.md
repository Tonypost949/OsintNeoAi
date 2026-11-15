# Master Mobile Handoff & Forensic Timeline Task Ledger
**Created:** September 17, 2026 | **Source:** Mobile Handoff https://share.gemini.google/lUC9lGA0dX8Z

## 1. Mobile Auth Tunnel Verification & Tokenization
- [ ] Verify gent/auth_helper.py and gent/oauth_server.py integration.
- [ ] Connect VS Code Tunnel / JetBrains Gateway SSH bridge for mobile authentication.

## 2. Automated Google Takeout / Mobile Evidence Ingestion
- [ ] Connect live mobile OAuth tokens with scripts/etp_master_takeout_pipeline.py.
- [ ] Ingest mobile screenshots and GPS EXIF metadata into central queue.

## 3. Forensic Timeline Graph Extraction
- [ ] Parse MASSACHUSETTS_COUNTERFEIT_PILL_FORENSIC_TIMELINE.md into structured JSON/CSV.
- [ ] Map 2020-2024 nodes (North Shore, Duxbury, Whitman) into core forensic graph.

## 4. BigQuery Relational Cross-Referencing
- [ ] Run relational queries against 
oble-beanbag-497411-m4 datasets.
- [ ] Flag temporal/geographical overlaps with mobile GPS metadata.

## 5. Dashboard Compilation & Web Deployment
- [ ] Consolidate graph data into web/ frontend.
- [ ] Push 3D MapLibre extrusions to osintneoai.me production domain.
