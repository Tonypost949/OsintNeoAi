# Implementation Plan: OSINTNeoAI & TaxFunded Master Architecture

## Overview
Full implementation of the **Single Engine / One Brain** architecture for OSINTNeoAI and TaxFunded: a 100% free-access, cloud-hosted investigative intelligence ecosystem featuring zero user footprint, 3 concurrent active investigations, omnichannel evasive ingestion, immutable dual-ledger cryptographic tracking, broadsheet newspaper and crossword reward generation, and automated BigQuery graph correlation.

---

## Architecture Decisions & Core Doctrine

1. **The "Single Engine / One Brain" Doctrine:**
   - One central intelligence engine; unique receptors (AI Chat, Chrome Extension `tab-copy`, Manual Input) sharing the exact same underlying nerves and core ingestion pipeline.
   - Zero physical duplication: Data is referenced virtually via metadata pointers across ledgers.

2. **100% Free Citizen Access & Zero Entry Paywalls:**
   - Users never pay fees to submit data.
   - Users can run up to **3 active investigations** simultaneously with generous daily token buckets (50k tokens/day).
   - All submissions (whistleblower evidence, research notes, duplicate text, or creative fiction) hit the ledger queue with an initial baseline value of **`ledger_value: 0`**.

3. **Evasive OSINT & Anonymity Protection:**
   - Aggressive metadata stripping (IP addresses, User-Agents, EXIF tags) before data reaches ledger tools.
   - Client receives a deterministic SHA-256 cryptographic receipt hash (`0x...`) proving submission provenance without exposing real-world identity.

4. **Dual Blockchain Ledgers & Token Rewards:**
   - **Ledger 1 (TaxFunded / `TFT`):** Federal and California municipal grants, taxpayer waste, public integrity audits. Triggers dual rewards (`TFT` + `OSINT`).
   - **Ledger 2 (OSINTNeoAI / `OSINT`):** Private corporate fraud, environmental EDRs, private LLC networks. Triggers `OSINT` rewards.

5. **Gamified Broadsheet & Crossword Engine:**
   - Newspaper publishing engine (*The Tax-Funded Dispatch*).
   - Interactive investigative crossword distributing testnet/smart contract crypto rewards (`TFT`).

---

## Task List

### Phase 1: Foundation & Ingestion Pipeline
- [x] **Task 1: Master OSINT Evidence Registry Harmonization**
  - Compiled 199 verified records across user nodes, FCA/RICO dockets, target accounts, BigQuery clusters, and infra audits into `data/MASTER_OSINT_EVIDENCE_REGISTRY.csv`.
- [x] **Task 2: BigQuery Master DDL & Replication Setup**
  - Generated `data/create_master_osint_evidence_registry_table.sql` for `noble-beanbag-497411-m4.national_audits.master_osint_evidence_registry`.
- [x] **Task 3: Zero-Value Append-Only Ingestion Endpoints**
  - Deployed `POST /api/ingest` and `GET /api/lookup_hash` on Port 10000 with `data/staging/` queue.

### Checkpoint: Foundation
- [x] Master registry verified (199 rows)
- [x] BigQuery schema validated
- [x] Server responding on Port 10000 with zero errors

---

### Phase 2: User Interfaces & Experience Layer
- [x] **Task 4: 3-Investigation Limiter & Session Manager**
  - Implemented `public/investigation_limiter.js` enforcing 3 active dossiers and daily 50k token allowance.
- [x] **Task 5: Investigator Chat HUD with Client-Side SHA-256**
  - Upgraded `public/workspace_chat.html` to hash payloads in-browser and stream instant receipt hashes with valuation links.
- [x] **Task 6: TaxFunded Read-Only Explorer & Fallback Ingestion**
  - Deployed `public/taxfunded_tracker.html` on `http://localhost:10000/taxfunded` with receipt hash valuation lookup.
- [x] **Task 7: The Chronicle Forensic Crypto Crossword**
  - Built `public/crypto_crossword.html` on `http://localhost:10000/crossword` with automated 50 TFT prize dispensing.
- [x] **Task 8: Live Interactive Master Sheet Viewer**
  - Deployed `public/master_osint_sheet_viewer.html` on `http://localhost:10000/sheet` with search, category filtering, and CSV export.

### Checkpoint: Core Features
- [x] Chat, Master Sheet, TaxFunded Explorer, and Crossword live on Port 10000
- [x] Client SHA-256 generation and `/api/ingest` pipeline operational end-to-end

---

### Phase 3: Background Intelligence & Valuation Automation
- [x] **Task 9: Autonomous Continuous Valuation Daemon**
  - Configured `scripts/autonomous_enrichment_worker.py` (`task-1288`) to continuously sweep `data/staging/`, cross-reference the 199 master entities, and elevate verified submissions to `CORROBORATED` status.
- [ ] **Task 10: Dynamic Daily Crossword Generator**
  - Build automated rotational puzzle generator pulling clues from new BigQuery evidence hits.
- [ ] **Task 11: E-Fax & Regulatory Hardmail Dispatch Connector**
  - Implement automated PDF complaint generator and eFax webhook hook for formal whistleblower submissions.

### Checkpoint: Complete
- [x] Dual-location backups verified (GitHub `main` + Google Drive `Sharedall/OsintNeoAi/`)
- [ ] Full end-to-end integration verified across all 11 tasks

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
| :--- | :---: | :--- |
| **Spam / Fiction Ingestion Flooding** | Low | All raw data enters at `ledger_value: 0` in lightweight off-chain JSON staging; costs zero compute until background worker matches graph. |
| **User Identity Exposure** | High | Metadata stripping middleware removes IPs, EXIF, and User-Agents before writing to ledger. |
| **BigQuery API Rate/Quota Limits** | Medium | Batched asynchronous worker loops (60s cycles) avoid continuous high-frequency query bursts. |
| **Data Loss / State Corruption** | High | Strict 2-Location backup policy: Git `main` commit checkpoints + Google Drive live `rclone` replica. Local 3GB zip backup disabled. |
