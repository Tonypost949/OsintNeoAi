# Plan — Orchestrator Gen 2 (orchestrator_3)

## Objective
Drive the OsintNeoAi Indexer and Timeline Reconciliation Pipeline through completion across Milestone 3, E2E Testing Suite (Tiers 1-4, `TEST_INFRA.md`, `TEST_READY.md`), Milestone 4 (Full E2E corpus execution, 100% Invariant Verification, Tier 5 Adversarial Hardening), Forensic Audit, and 3-Location Backup Protocol per `AGENTS.md`.

## Execution Steps

### Phase 1: M3 Implementation Verification & E2E Testing Suite Track
- **Step 1.1**: Dispatch `test_writer_e2e` to author `test_tier3_combinations.py`, `test_tier4_scenarios.py`, `test_indexer_invariants.py`, `TEST_INFRA.md`, and `TEST_READY.md` in `C:\OsintNeoAi\workspaces\osintneoai_indexer\`.
- **Step 1.2**: Dispatch `worker_m3_r1` or `reviewer_m3_1` / `reviewer_m3_2` to test and verify `resolution/taxonomy.py`, `resolution/entity_resolver.py`, `storage/vault_db.py`, `storage/catalog_exporter.py`, `pipeline.py`, and run `tests/test_m3_resolution_storage.py`.

### Phase 2: M3 & E2E Gate Verification
- **Step 2.1**: Dispatch `challenger_1` and `challenger_2` to stress-test M3 and E2E pipelines (phonetic edge cases, large graphs, malformed dates/currencies, database transactions, Merkle root consistency).
- **Step 2.2**: Dispatch `auditor_1` to perform forensic integrity audit across M1-M3 codebase.
- **Step 2.3**: Gate evaluation for M3 and E2E Testing Track in `GATE_STATUS.md`.

### Phase 3: Milestone 4 Full Pipeline Execution & 100% Invariant Verification
- **Step 3.1**: Dispatch Worker to run `pipeline.py` over target evidence corpus (`C:\OsintNeoAi\evidence\official_court_records\` and local files) generating `timeline_vault.db` and `master_timeline_catalog.json`.
- **Step 3.2**: Execute the complete automated pytest suite across all tiers (`test_m1_ingestion.py`, `test_m2_extraction.py`, `test_m3_resolution_storage.py`, `test_tier1_features.py`, `test_tier2_boundaries.py`, `test_tier3_combinations.py`, `test_tier4_scenarios.py`, `test_indexer_invariants.py`).
- **Step 3.3**: Final Forensic Integrity Audit (`victory_auditor_1`).

### Phase 4: 3-Location Backup & Final Reporting
- **Step 4.1**: Dispatch `worker_git_backup_1` to execute and verify the 3-location backup protocol per `C:\OsintNeoAi\AGENTS.md` (GitHub origin/main, Local C:\ OneDrive backup, Sharedall Google Drive via rclone).
- **Step 4.2**: Synthesize final verification report and deliver to Sentinel via `send_message`.
