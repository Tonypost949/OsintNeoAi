## 2026-08-29T18:12:08Z
You are the Implementation Worker for Milestone 3 (M3: Entity Resolution, SQLite Relational Vault & Master JSON Catalog, and End-to-End Pipeline) of the OsintNeoAi Indexer project.
Your Working Directory: C:\OsintNeoAi\.agents\worker_m3_r1\
Target Workspace: C:\OsintNeoAi\workspaces\osintneoai_indexer\

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Read authoritative files first:
1. C:\OsintNeoAi\.agents\ORIGINAL_REQUEST.md (specifically ## 2026-08-29T17:34:35Z)
2. C:\OsintNeoAi\PROJECT.md (M3 Scope, Features 12-15, Interface Contracts, Code Layout)
3. C:\OsintNeoAi\AGENTS.md
4. Architecture blueprint: C:\OsintNeoAi\.agents\explorer_survey_3\analysis.md (DDL, Entity Taxonomy, Disjoint Set Union clustering, JSON Schema, Merkle tree)
5. Existing M1 and M2 implementations in C:\OsintNeoAi\workspaces\osintneoai_indexer\

Files You Exclusively Own & Must Implement:
- C:\OsintNeoAi\workspaces\osintneoai_indexer\resolution\__init__.py
- C:\OsintNeoAi\workspaces\osintneoai_indexer\resolution\taxonomy.py
- C:\OsintNeoAi\workspaces\osintneoai_indexer\resolution\entity_resolver.py
- C:\OsintNeoAi\workspaces\osintneoai_indexer\storage\vault_db.py
- C:\OsintNeoAi\workspaces\osintneoai_indexer\storage\catalog_exporter.py
- C:\OsintNeoAi\workspaces\osintneoai_indexer\pipeline.py
- C:\OsintNeoAi\workspaces\osintneoai_indexer\tests\test_m3_resolution_storage.py

Requirements & Acceptance Criteria:
1. `resolution/taxonomy.py`: Implement the 6 entity categories (`INDIVIDUAL`, `MUNICIPAL_BODY`, `FINANCIAL_INSTITUTION`, `PROPERTY_MANAGEMENT`, `LEGAL_AGENCY`, `COMMERCIAL_ENTITY`), entity dataclass, confidence scoring, and canonical entities map for primary investigation targets.
2. `resolution/entity_resolver.py`: Implement 4-stage entity resolution pipeline (Normalization, Corporate Suffix Stripping, Phonetic Blocking with Russell Soundex / Double Metaphone, Contextual Jaro-Winkler Matching, Disjoint-Set Union / DSU clustering).
3. `storage/vault_db.py`: Implement SQLite database manager for `timeline_vault.db` with 3NF relational schema (tables: `documents`, `entities`, `entity_mentions`, `timeline_events`, `financial_transactions`, `relationships`, `schema_invariants_log`), WAL journal mode, strict foreign key enforcement, indexing on sha256/dates/entities, and atomic transaction batches.
4. `storage/catalog_exporter.py`: Implement RFC 8785 canonical JSON master catalog generator `master_timeline_catalog.json` with embedded Merkle root cryptographic hash tree, chronological event sorting, and summary metrics.
5. `pipeline.py`: Implement the unified CLI and execution pipeline (`OsintNeoAiIndexerPipeline`) connecting LocalCrawler/GDriveStreamer -> DocumentExtractor -> Normalizers -> EntityResolver -> VaultDB -> CatalogExporter. Support processing input directories (`C:\Users\Amd949609\Downloads`, `C:\OsintNeoAi\evidence`), limit caps, and generate `timeline_vault.db` and `master_timeline_catalog.json` in `C:\OsintNeoAi\workspaces\osintneoai_indexer\`.
6. Implement comprehensive tests in `tests/test_m3_resolution_storage.py` and run `pytest`. Ensure 100% of tests pass.
7. Write a comprehensive 5-component handoff report to `C:\OsintNeoAi\.agents\worker_m3_r1\handoff.md` and send a completion message to the parent orchestrator (34f685b0-e5c3-4fa3-aac5-dc635a0add4e).
