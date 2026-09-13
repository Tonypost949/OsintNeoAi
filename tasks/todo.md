# Master Task Checklist: OSINTNeoAI & TaxFunded Architecture

## Phase 1: Foundation & Ingestion Pipeline
- [x] **Task 1: Master OSINT Evidence Registry Harmonization**
  - Compiled 199 verified records into `data/MASTER_OSINT_EVIDENCE_REGISTRY.csv` and `data/MASTER_OSINT_EVIDENCE_REGISTRY.json`.
- [x] **Task 2: BigQuery Master DDL & Replication Setup**
  - Generated `data/create_master_osint_evidence_registry_table.sql` for `noble-beanbag-497411-m4.national_audits.master_osint_evidence_registry`.
- [x] **Task 3: Zero-Value Append-Only Ingestion Endpoints**
  - Deployed `POST /api/ingest` and `GET /api/lookup_hash` on Port 10000 with `data/staging/` queue.

## Checkpoint 1: Foundation
- [x] Verified 199 master records harmonized
- [x] BigQuery DDL validated
- [x] Local map server responding on Port 10000

---

## Phase 2: User Interfaces & Experience Layer
- [x] **Task 4: 3-Investigation Limiter & Session Manager**
  - Implemented `public/investigation_limiter.js` enforcing 3 active dossiers and daily 50k token allowance.
- [x] **Task 5: Investigator Chat HUD with Client-Side SHA-256**
  - Upgraded `public/workspace_chat.html` with in-browser SHA-256 hashing, instant receipt badges, and `/taxfunded` lookup links.
- [x] **Task 6: TaxFunded Read-Only Explorer & Fallback Ingestion**
  - Deployed `public/taxfunded_tracker.html` on `http://localhost:10000/taxfunded` with receipt hash valuation lookup.
- [x] **Task 7: The Chronicle Forensic Crypto Crossword**
  - Built `public/crypto_crossword.html` on `http://localhost:10000/crossword` with automated 50 TFT prize dispensing.
- [x] **Task 8: Live Interactive Master Sheet Viewer**
  - Deployed `public/master_osint_sheet_viewer.html` on `http://localhost:10000/sheet` with search, category filtering, and CSV export.

## Checkpoint 2: Core Features
- [x] All 4 web interfaces live on Port 10000
- [x] Client SHA-256 generation and `/api/ingest` pipeline operational end-to-end

---

## Phase 3: Background Intelligence & Dispatch Automation
- [x] **Task 9: Autonomous Continuous Valuation Daemon**
  - Configured `scripts/autonomous_enrichment_worker.py` (`task-1288`) to continuously sweep `data/staging/`, cross-reference the 199 master entities, and elevate verified submissions to `CORROBORATED` status.
- [ ] **Task 10: Dynamic Daily Crossword Generator**
  - Build automated rotational puzzle generator pulling clues from new BigQuery evidence hits.
- [ ] **Task 11: E-Fax & Regulatory Hardmail Dispatch Connector**
  - Implement automated PDF complaint generator and eFax webhook hook for formal whistleblower submissions.

## Checkpoint 3: Complete
- [x] Dual-location backups verified (GitHub `main` + Google Drive `Sharedall/OsintNeoAi/`)
- [ ] Next feature sprint ready for user command
