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

## Next Agent Fleet Workstream Plan

### Starting Point
- The repository overview describes a multi-surface OSINT platform, including a web UI, API, BigQuery-backed workflows, and the existing crossword page.
- `TEST_READY.md` records 71/71 offline E2E tests passing on 2026-09-01. Treat this as a prior readiness result, not a current run; rerun the focused baseline before merging new work.
- The remaining roadmap items are Task 10 (dynamic crossword generation) and Task 11 (complaint PDF and e-fax dispatch). They can proceed as separate feature lanes.

### Phase 0: Coordinator Preflight
**Task F0: Establish the agent contract and baseline**
- Confirm the active branch/worktree and preserve unrelated working-tree changes.
- Run the existing offline baseline in `TEST_READY.md`; record any pre-existing failures.
- Agree that crossword data is limited to approved, publishable clues and that outbound faxing is disabled by default; use mocked/test delivery until an explicit authorization flow and provider configuration exist.
- **Acceptance:** baseline result is recorded; shared data contracts and non-goals are written into the task descriptions before implementation starts.
- **Verification:** `python -m pytest tests/test_autonomous_correlation_e2e.py -q`
- **Dependencies:** None. Must complete before agents modify files.

### Phase 1: Parallel Feature Lanes
**Lane A — Task F1: Dynamic daily crossword**
- Add a deterministic generator that consumes a defined, sanitized evidence/clue input and produces a validated puzzle in the format used by `public/crypto_crossword.html`.
- Preserve a fixture/offline path so generation tests do not require BigQuery credentials or live data.
- **Acceptance:** generated puzzles pass schema and clue/answer consistency checks; the page can load generated output without breaking its existing static puzzle behavior.
- **Verification:** add focused generator tests for empty, malformed, duplicate, and normal inputs; run the existing UI checks if available.
- **Dependencies:** F0. Independent of Lane B.

**Lane B — Task F2: Dispatch contract and approval boundary**
- Define a provider-neutral dispatch request/status contract, PDF input fields, audit metadata, and explicit approval state before splitting implementation.
- Do not auto-send complaints or enable a live fax provider by default.
- **Acceptance:** contract identifies required recipient/document metadata, validation failures, idempotency behavior, and the approval gate.
- **Verification:** unit tests cover invalid requests, duplicate requests, and unapproved dispatch rejection.
- **Dependencies:** F0. This contract is the prerequisite for F3 and F4.

### Phase 2: Parallel Dispatch Components
**Task F3: Complaint PDF generation**
- Generate a deterministic PDF from validated, user-approved content; keep generation separate from transmission.
- **Acceptance:** required fields are validated, generated PDF is readable and reproducible, and sensitive values are not written to logs.
- **Verification:** tests cover valid output, missing fields, malformed content, and temporary-file cleanup.
- **Dependencies:** F2.

**Task F4: E-fax provider adapter**
- Implement the provider-neutral adapter against the shared contract, with mocked transport by default and explicit approval required for dispatch.
- **Acceptance:** mocked success/failure responses map to stable statuses; retries cannot create duplicate sends; no credentials are required by offline tests.
- **Verification:** mocked tests cover timeout, provider rejection, retry/idempotency, and approval denial.
- **Dependencies:** F2. Can run in parallel with F3.

### Phase 3: Integration and Release Gate
**Task F5: End-to-end integration**
- Connect approved PDF creation to the dispatch adapter and document configuration/operations, keeping the live-send path opt-in.
- **Acceptance:** one offline end-to-end test covers request validation through mocked delivery; existing crossword/static behavior remains intact.
- **Verification:** run focused F1/F3/F4 tests and the `TEST_READY.md` baseline; review changed paths and confirm no live outbound calls occurred.
- **Dependencies:** F1, F3, and F4.

### Execution Order
```text
F0
├── F1 (crossword, independent)
└── F2 (dispatch contract)
    ├── F3 (PDF generation) ─┐
    └── F4 (fax adapter) ────┴── F5 (integration/release gate)
```

### Fleet Coordination and Risks
- Assign one agent per independent lane; avoid concurrent edits to shared files. The dispatch contract agent should publish the contract before F3/F4 start.
- Keep changes scoped to the crossword surface and new dispatch/PDF modules plus focused tests; do not refactor unrelated legacy directories.
- The recorded readiness result is dated and covers correlation features, not these two roadmap features. Re-run it for a current baseline, then add feature-specific tests rather than treating 71/71 as proof of new-feature readiness.
- Live evidence access, provider credentials, and permission to transmit are not prerequisites for offline implementation; if live dispatch is later requested, require explicit authorization and separate provider setup.
