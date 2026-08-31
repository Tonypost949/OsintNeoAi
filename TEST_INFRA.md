# OsintNeoAi Indexer Test Infrastructure Specification

**Document Version:** 1.0.0  
**Project:** OsintNeoAi Forensic Document Processing & Timeline Reconciliation Pipeline  
**Target Workspace:** `C:\OsintNeoAi\workspaces\osintneoai_indexer\`  
**Compliance Standard:** RFC 8785 JSON Canonicalization, SQLite 3NF Schema Invariants, SHA-256 Stream Integrity, ISO 8601 Temporal Monotonicity  

---

## 1. Testing Philosophy & Core Invariants

The OsintNeoAi Indexer processes evidentiary documents from high-stakes federal, state, and municipal investigations (e.g., Anaheim Angel Stadium public corruption, Orange County Unlawful Detainer court docket, and multi-state police/narcotics records). Because downstream consumers rely on these datasets for forensic auditing, whistleblower briefings, and courtroom-ready evidence presentation, the test infrastructure enforces zero-tolerance mathematical and evidentiary invariants:

1. **Deterministic Cryptographic Verification (SHA-256 & RFC 8785):**
   - Every raw artifact and extracted text stream is hashed using 64 KB block streaming SHA-256 algorithms.
   - All exported JSON structures adhere to RFC 8785 JSON Canonicalization Scheme (JCS), ensuring deterministic byte-for-byte serialization across platforms.
   - Master dataset state is cryptographically bound into a 256-bit hierarchical Merkle tree root.

2. **Strict Chronological Monotonicity & Causal Precedence:**
   - All timestamps parse into canonical ISO 8601 UTC representation (`YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SSZ`).
   - Timeline events must maintain strictly non-decreasing chronological order when ordered by rank.
   - Causal sequence invariants are verified (e.g., Regulatory Notices precede Council Voidance Resolutions; FBI Search Warrant Affidavits precede Guilty Pleas).

3. **Relational Vault Integrity (SQLite 3NF):**
   - Foreign key integrity is unconditionally enforced (`PRAGMA foreign_keys = ON;`).
   - `PRAGMA foreign_key_check;` must return 0 violations across all tables.
   - Unique constraints prevent duplicate document ingestion by `file_sha256`.
   - Graph relationships disallow self-loops (`source_entity_id <> target_entity_id`).

4. **Financial Conservatism & Precision:**
   - Monetary amounts are parsed into exact float and integer cents representations.
   - Financial transactions require strictly non-negative values (`amount >= 0.0`).
   - Complex multipliers (`$320M`, `$96M`, `$50K`) and accounting parentheses `($10,000)` evaluate to exact mathematical values.

5. **Opaque-Box & Multi-Tier Independence:**
   - Tests do not assume or rely on external cloud dependencies; all fixtures are fully isolated, reproducible, and self-contained.
   - Synthetic corpora mirror real-world forensic challenges (degraded OCR, skewed scans, Unicode surrogates, adversarial edge cases).

---

## 2. Four-Tier Testing Methodology

The test suite is structured into four progressive validation tiers plus a dedicated Invariant Verification suite:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ TIER 4: Real-World Investigative Scenarios (>= 9 E2E Workload Scenarios)     │
│ End-to-end pipeline execution on domain corpora (Angel Stadium, Eviction)    │
├──────────────────────────────────────────────────────────────────────────────┤
│ TIER 3: Cross-Feature Pairwise Combinations (>= 17 Integration Tests)         │
│ Pairwise integration across connectors, extractors, normalizers, vault & JSON│
├──────────────────────────────────────────────────────────────────────────────┤
│ TIER 2: Comprehensive Boundary & Corner Cases (>= 85 Boundary Tests)         │
│ 5+ edge tests per feature (empty files, corrupt streams, extreme values)     │
├──────────────────────────────────────────────────────────────────────────────┤
│ TIER 1: Feature Unit Tests (>= 85 Unit Tests)                                │
│ 5+ exhaustive unit tests per feature across all 17 features                  │
├──────────────────────────────────────────────────────────────────────────────┤
│ INVARIANTS: Cryptographic & Relational Invariant Suite                       │
│ FK checks, Merkle tree reduction, monotonic event ranking, schema checks     │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Tier Definitions

- **Tier 1: Feature Unit Tests (`test_tier1_features.py`)**
  - Scope: Exhaustive unit test coverage for every functional component.
  - Requirement: At least 5 non-trivial unit tests per feature across all 17 features (Minimum 85 tests).
  - Validation: Exact return values, dataclass contracts, regex matching precision, normalizer logic, and DDL execution.

- **Tier 2: Boundary & Corner Cases (`test_tier2_boundaries.py`)**
  - Scope: Robustness under stress, anomalous inputs, and adversarial conditions.
  - Requirement: At least 5 boundary/corner tests per feature across all 17 features (Minimum 85 tests).
  - Validation: Zero-byte files, massive 100MB+ virtual streams, Unicode surrogate pairs, corrupt ZIP/PDF headers, missing dates, malformed JSON, and concurrent DB locks.

- **Tier 3: Cross-Feature Combinations (`test_tier3_combinations.py`)**
  - Scope: Pairwise and multi-module integration across pipeline stages.
  - Requirement: At least 17 cross-feature integration tests covering interface handoffs (e.g., Crawler -> Extractor -> Normalizer -> Resolver -> Vault -> Exporter).
  - Validation: Data fidelity across transformations, cascade deletions, alias resolution linking to timeline events, and financial reconciliation.

- **Tier 4: Real-World Scenarios (`test_tier4_scenarios.py`)**
  - Scope: End-to-end investigative workload scenarios mirroring active federal and state cases.
  - Requirement: At least 9 comprehensive domain scenarios:
    1. *Angel Stadium Public Corruption Inquiry* (HCD SLA Violation, Council Resolution 2022-064, Sidhu Plea).
    2. *Orange County Unlawful Detainer Docket* (Woodbridge Meadows v. Dimarcello, 61 ROAs, Triple Default Judgments, 170.6 Strike).
    3. *Interstate Logistics & Law Enforcement Incident Logs* (Hamilton NJ Police logs, Ewing PD chain of custody, Quantum Auto Dismantler).
    4. *Slush Fund & Political Conduit Flow* (TA Group, FPS Strategies, Chamber of Commerce $320M to $1.5M diversion).
    5. *Degraded Document & OCR Recovery Pipeline* (Low-contrast, skewed, noise-corrupted scanned exhibits).
    6. *Multi-Source GDrive and Local Archive Ingestion* (Mixed ZIP archives, EML headers, PDF briefs, DOCX contracts).
    7. *Phonetic Alias Resolution & Entity Disambiguation* (OCR variations: Sldhu -> Sidhu, Melahat Rafiei -> Melahat Rafie).
    8. *Whistleblower Retaliation & Timeline Reconstruction* (Chronological reconstruction of personnel and retaliatory actions).
    9. *Full Vault Database to Master JSON Catalog Export* (Complete end-to-end catalog generation with Merkle verification).

- **Indexer Invariant Suite (`test_indexer_invariants.py`)**
  - Scope: Continuous mathematical verification of database consistency, Merkle tree calculations, and chronological ordering.
  - Requirement: Verification of `PRAGMA foreign_key_check`, zero hash collisions, chronological monotonic order, non-negative monetary amounts, and Merkle root determinism.

---

## 3. Feature Coverage Matrix (All 17 Features)

| # | Feature Name | Primary Module | Tier 1 (Unit) | Tier 2 (Boundary) | Tier 3 (Integration) | Tier 4 (Scenario) | Invariant Check |
|---|---|---|:---:|:---:|:---:|:---:|:---:|
| 1 | Stream Ingestion & Chunking | `connectors.local_crawler` | 5 | 5 | Yes | Yes | Zero Memory Leaks |
| 2 | Google Drive Link Resolver | `connectors.gdrive_streamer` | 5 | 5 | Yes | Yes | Spool Cleanup |
| 3 | Cryptographic SHA-256 Engine | `storage.hasher` | 5 | 5 | Yes | Yes | 64KB Block Streaming |
| 4 | Multi-Format MIME Dispatcher | `config`, `connectors` | 5 | 5 | Yes | Yes | Magic Byte Sniffing |
| 5 | Native Digital Text Extraction | `extractors.format_extractors` | 5 | 5 | Yes | Yes | Density Check |
| 6 | Neural Offline OCR Engine | `extractors.ocr_engine` | 5 | 5 | Yes | Yes | Reading Order |
| 7 | Image Preprocessing & Enhancement | `extractors.image_enhancer` | 5 | 5 | Yes | Yes | CLAHE & Deskew |
| 8 | Timestamp Normalizer | `normalizers.date_normalizer` | 5 | 5 | Yes | Yes | ISO 8601 Format |
| 9 | Financial Transaction Normalizer | `normalizers.financial_normalizer` | 5 | 5 | Yes | Yes | Dual Float + Cents |
| 10 | Legal Case Identifier Normalizer | `normalizers.case_normalizer` | 5 | 5 | Yes | Yes | Docket Precision |
| 11 | Communication Metadata Normalizer | `normalizers.entity_normalizer`, `connectors.mailbox_reader` | 5 | 5 | Yes | Yes | RFC 2047 Decoding |
| 12 | 6-Category Entity Extractor | `resolution.taxonomy`, `resolution.entity_resolver` | 5 | 5 | Yes | Yes | Taxonomy Adherence |
| 13 | Phonetic & Contextual Entity Resolver | `resolution.entity_resolver`, `normalizers.entity_normalizer` | 5 | 5 | Yes | Yes | DSU Graph Cluster |
| 14 | SQLite Relational Vault | `storage.vault_db` | 5 | 5 | Yes | Yes | PRAGMA FK = 0 |
| 15 | Master JSON Catalog Exporter | `storage.catalog_exporter` | 5 | 5 | Yes | Yes | RFC 8785 & Merkle |
| 16 | E2E Test Suite (Tiers 1–4) | `tests.conftest`, `tests.*` | 5 | 5 | Yes | Yes | Fixture Isolation |
| 17 | 100% Invariant Verification & Hardening | `pipeline`, `storage.catalog_exporter` | 5 | 5 | Yes | Yes | Master Root Hash |

---

## 4. Test Suite Execution & Runner Commands

### 4.1 Running the Full Test Suite
To execute all tests with detailed verbosity and summary reporting:
```powershell
python -m pytest C:\OsintNeoAi\workspaces\osintneoai_indexer\tests\ -v
```

### 4.2 Running Specific Test Tiers
```powershell
# Tier 1: Feature Unit Tests (85 tests)
python -m pytest C:\OsintNeoAi\workspaces\osintneoai_indexer\tests\test_tier1_features.py -v

# Tier 2: Boundary & Corner Cases (85 tests)
python -m pytest C:\OsintNeoAi\workspaces\osintneoai_indexer\tests\test_tier2_boundaries.py -v

# Tier 3: Cross-Feature Integration Tests (17+ tests)
python -m pytest C:\OsintNeoAi\workspaces\osintneoai_indexer\tests\test_tier3_combinations.py -v

# Tier 4: Real-World E2E Scenarios (9+ scenarios)
python -m pytest C:\OsintNeoAi\workspaces\osintneoai_indexer\tests\test_tier4_scenarios.py -v

# Invariants Suite: Schema, Crypto & Ordering Invariants
python -m pytest C:\OsintNeoAi\workspaces\osintneoai_indexer\tests\test_indexer_invariants.py -v
```

### 4.3 Running with Fail-Fast & Short Traceback
```powershell
python -m pytest C:\OsintNeoAi\workspaces\osintneoai_indexer\tests\ -x --tb=short
```

### 4.4 Automated Standalone Verification
The pipeline CLI entrypoint also supports direct invariant audit execution:
```powershell
python C:\OsintNeoAi\workspaces\osintneoai_indexer\pipeline.py --verify-only
```
