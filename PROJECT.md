# Project: OsintNeoAi Indexer & Timeline Reconciliation Pipeline

## Architecture
The OsintNeoAi Indexer is a modular, high-throughput, memory-bounded forensic ingestion and timeline reconciliation pipeline. It processes multi-format archives (PDF, TIFF, PNG, JPG, HTML, DOCX, MBOX, TXT, ZIP) from local directories (`C:\Users\Amd949609\Downloads`, `C:\OsintNeoAi\evidence`) and external Google Drive links, executing neural/offline OCR, extracting entities and chronological events, and generating a normalized SQLite database (`timeline_vault.db`) and structured JSON master catalog (`master_timeline_catalog.json`) with 100% cryptographic SHA-256 verification.

### System Data Flow
```
[Local Archives / GDrive] ──> [Stream Ingest & Chunking] ──> [SHA-256 Hasher]
                                       │
                                       ▼
                         [MIME & Format Dispatcher]
                                       │
            ┌──────────────────────────┴──────────────────────────┐
            ▼                                                     ▼
  [Digital Text Extractor]                              [Scanned / Image OCR]
    (PyMuPDF, HTML, DOCX)                               (RapidOCR ONNX, OpenCV)
            └──────────────────────────┬──────────────────────────┘
                                       │
                                       ▼
                          [Multi-Tier Normalizer]
                 (ISO 8601 Dates, Currency Cents, Case IDs)
                                       │
                                       ▼
                       [Entity Extractor & Resolver]
                   (6-Taxonomy, Phonetic Blocking, DSU)
                                       │
            ┌──────────────────────────┴──────────────────────────┐
            ▼                                                     ▼
   [SQLite Relational Vault]                             [Master JSON Catalog]
   (timeline_vault.db, 3NF)                           (master_timeline_catalog.json)
            └──────────────────────────┬──────────────────────────┘
                                       │
                                       ▼
                           [Invariant Verification]
                      (100% pytest suite, SHA-256 audit)
```

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Stream Ingestion & Chunking | Memory-bounded ($O(1)$ RAM) streaming ingestion for large archives, zip files, and directories | M1 | Survey R1 |
| 2 | Google Drive Link Resolver | Chunked streaming resolver and downloader for public/shared Google Drive URLs with virus-scan bypass | M1 | Survey R1 |
| 3 | Cryptographic SHA-256 Engine | Continuous 64 KB block streaming SHA-256 hasher for every raw file and extracted artifact | M1 | Survey R4 |
| 4 | Multi-Format MIME Dispatcher | Format-specific dispatcher handling PDF, TIFF, PNG, JPG, HTML, DOCX, MBOX/EML, TXT, CSV, JSON | M1 | Survey R1 |
| 5 | Native Digital Text Extraction | High-speed PyMuPDF text extraction with density threshold checks | M2 | Survey R2 |
| 6 | Neural Offline OCR Engine | CPU-optimized RapidOCR ONNX neural text recognition with multi-page pixmap rendering | M2 | Survey R2 |
| 7 | Image Preprocessing & Enhancement | OpenCV CLAHE adaptive contrast and thresholding for low-contrast/degraded documents | M2 | Survey R2 |
| 8 | Timestamp Normalizer | Regex and fuzzy parsing of all historical and legal dates to canonical ISO 8601 UTC (`YYYY-MM-DD` / `YYYY-MM-DDTHH:MM:SSZ`) | M2 | Survey R2 |
| 9 | Financial Transaction Normalizer | Monetary parser converting $ amounts, expressions ($M, $k), and accounting parentheses to dual float and integer cents | M2 | Survey R2 |
| 10 | Legal Case Identifier Normalizer | Federal (USDC CDCA/DNJ) and state (CA Superior Court) docket and statutory citation extractor | M2 | Survey R2 |
| 11 | Communication Metadata Normalizer | Sender/recipient, subject, email header, and participant metadata extractor | M2 | Survey R2 |
| 12 | 6-Category Entity Extractor | Rule-based and keyword-driven entity extraction (Individuals, Municipalities, Financial, Property, Legal, Commercial) | M3 | Survey R3 |
| 13 | Phonetic & Contextual Entity Resolver | Multi-pass entity disambiguation (Soundex, Double Metaphone, Jaro-Winkler, Disjoint Set Union clustering) | M3 | Survey R3 |
| 14 | SQLite Relational Vault | 3NF SQLite database (`timeline_vault.db`) with WAL mode, foreign keys, indexes, and full relational tables | M3 | Survey R3 |
| 15 | Master JSON Catalog Exporter | Structured RFC 8785 compliant `master_timeline_catalog.json` with embedded Merkle root cryptographic signatures | M3 | Survey R3 |
| 16 | E2E Test Suite (Tiers 1–4) | Comprehensive opaque-box test suite (Tier 1: Feature, Tier 2: Boundary, Tier 3: Combinatorial, Tier 4: Real-World) | E2E-TEST | Survey R4 |
| 17 | 100% Invariant Verification & Hardening | Invariant test execution against pipeline deliverables and Tier 5 adversarial stress testing | M4 | Survey R4 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| E2E | E2E Testing Suite | Opaque-box E2E test harness, fixtures, runners, and Tiers 1-4 tests (produces TEST_INFRA.md & TEST_READY.md) | none | IN_PROGRESS |
| M1 | Ingestion & Streaming Engine | Local archive crawler, Google Drive chunked streamer, 64KB block SHA-256 hasher, MIME dispatcher | none | DONE |
| M2 | Deep Text Extraction & OCR Engine | 5-tier extraction/OCR ladder (PyMuPDF, RapidOCR ONNX, CLAHE), ISO 8601, financial cents, case dockets | M1 | IN_PROGRESS |
| M3 | Entity Resolution & Vault Storage | 6-category entity taxonomy, phonetic/DSU resolver, SQLite timeline_vault.db, master_timeline_catalog.json | M2 | PLANNED |
| M4 | Final E2E Pass & Adversarial Hardening | Pass 100% of E2E test suite (Tiers 1-4), Tier 5 white-box adversarial stress tests, backup protocol check | M3, E2E | PLANNED |

## Interface Contracts

### M1 ↔ M2: Ingestion Stream to Document Extractor
```python
from dataclasses import dataclass
from typing import Generator, Optional, BinaryIO

@dataclass(frozen=True)
class IngestedArtifact:
    artifact_id: str             # Canonical SHA-256 hex string
    source_uri: str              # File path or remote URL
    mime_type: str               # Canonical MIME type (e.g. 'application/pdf')
    file_size_bytes: int         # Exact file size
    raw_stream_factory: callable # Callable returning a fresh BinaryIO stream
```

### M2 ↔ M3: Extraction Result to Entity Resolution & Storage
```python
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class ExtractedRecord:
    record_id: str               # UUID or deterministic artifact-derived ID
    artifact_sha256: str         # SHA-256 of source file
    source_path: str             # Source URI / path
    source_type: str             # 'local_file', 'gdrive', 'mailbox', etc.
    mime_type: str               # MIME type
    normalized_date: Optional[str] # ISO 8601 UTC date string (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ)
    raw_date_string: Optional[str]
    extracted_text: str          # Normalized text body
    ocr_engine_used: str         # 'pymupdf_native', 'rapidocr_onnx', 'html_parser', etc.
    financial_amounts: List[Dict[str, Any]] # [{"raw": "$320M", "amount_float": 320000000.0, "amount_cents": 32000000000, "currency": "USD"}]
    case_numbers: List[str]      # ["8:23-cr-00108-CJC", "30-2021-01201327-CL-UD-CJC"]
    sender: Optional[str]
    recipients: List[str]
    metadata: Dict[str, Any]
```

### M3 ↔ M4 & E2E: Database & Catalog Deliverables
```
SQLite Vault: C:\OsintNeoAi\workspaces\osintneoai_indexer\timeline_vault.db
- Tables:
  - documents (document_id PK, sha256 UNIQUE, file_path, mime_type, file_size, ingestion_timestamp, page_count)
  - entities (entity_id PK, canonical_name, entity_type, aliases_json, confidence_score)
  - entity_mentions (mention_id PK, entity_id FK, document_id FK, raw_text, context_snippet, confidence)
  - timeline_events (event_id PK, document_id FK, event_date ISO8601, event_title, event_description, significance_score)
  - financial_transactions (transaction_id PK, document_id FK, transaction_date, amount_float, amount_cents, currency, payer, payee, description)
  - relationships (relationship_id PK, source_entity_id FK, target_entity_id FK, relation_type, document_id FK, confidence)

Master Catalog: C:\OsintNeoAi\workspaces\osintneoai_indexer\master_timeline_catalog.json
- Top-level Keys:
  - catalog_version: "1.0.0"
  - generated_at: ISO 8601 UTC timestamp
  - merkle_root: SHA-256 hex string
  - summary: { total_documents: int, total_entities: int, total_events: int, total_financial_transactions: int }
  - documents: List[DocumentRecord]
  - entities: List[EntityRecord]
  - timeline_events: List[TimelineEventRecord] (chronologically sorted)
  - financial_transactions: List[FinancialTransactionRecord]
  - relationships: List[RelationshipRecord]
```

## Code Layout
```
C:\OsintNeoAi\workspaces\osintneoai_indexer\
├── __init__.py
├── pipeline.py                      # Main entrypoint and pipeline orchestrator
├── config.py                        # Pipeline configuration, paths, and constants
├── connectors/
│   ├── __init__.py
│   ├── local_crawler.py             # Streaming local archive crawler
│   ├── gdrive_streamer.py           # Chunked Google Drive stream downloader
│   └── mailbox_reader.py            # Streaming MBOX / EML parser
├── extractors/
│   ├── __init__.py
│   ├── document_extractor.py        # 5-Tier Fallback Ladder (PyMuPDF -> RapidOCR -> OpenCV -> Format parsers)
│   ├── ocr_engine.py                # RapidOCR ONNX runtime integration
│   └── image_enhancer.py            # OpenCV CLAHE and thresholding
├── normalizers/
│   ├── __init__.py
│   ├── date_normalizer.py           # ISO 8601 UTC timestamp parser
│   ├── financial_normalizer.py      # Monetary amount parser (dual float + cents)
│   ├── case_normalizer.py           # Federal & CA Superior Court docket matcher
│   └── entity_normalizer.py         # Corporate suffix cleaner & phonetic encoder
├── resolution/
│   ├── __init__.py
│   ├── entity_resolver.py           # 6-category entity extractor, blocking & DSU clustering
│   └── taxonomy.py                  # Entity categories and classification schemas
├── storage/
│   ├── __init__.py
│   ├── vault_db.py                  # SQLite database manager, schema DDL, WAL & indexes
│   ├── catalog_exporter.py          # Master JSON catalog generator & Merkle root calculator
│   └── hasher.py                    # 64 KB block streaming SHA-256 engine
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  # Pytest fixtures and test configuration
│   ├── test_tier1_features.py       # Tier 1: Feature unit tests (5 per feature)
│   ├── test_tier2_boundaries.py     # Tier 2: Boundary & corner case tests (5 per feature)
│   ├── test_tier3_combinations.py   # Tier 3: Cross-feature pairwise tests
│   ├── test_tier4_scenarios.py      # Tier 4: Real-world end-to-end workload scenarios
│   └── test_indexer_invariants.py   # R4 Invariant validation suite (schema, crypto, ordering)
├── timeline_vault.db                # Generated SQLite database
└── master_timeline_catalog.json     # Generated Master JSON Catalog
```
