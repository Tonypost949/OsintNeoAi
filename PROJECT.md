# Project: OsintNeoAi Autonomous Forensic & OSINT Synchronization Engine

## Architecture
The system is an autonomous, end-to-end intelligence engine designed for live Master OSINT Sheet synchronization (40 tabs), multi-format evidence ingestion, neural OCR extraction, topological entity resolution, BigQuery graph correlation, multi-channel reporting, and strict 3-location backup synchronization.

```
[Master OSINT Sheet (40 Tabs)] ←→ [Master Sync & Entity Normalizer]
                                              │
[Multi-Source Evidence (PDF/Img/Zips)] ──→ [Neural OCR & Stream Hasher (RapidOCR / PyMuPDF)]
                                              │
                                              ▼
                             [Topological Entity Resolver & SQLite 3NF Vault]
                                              │
                  ┌───────────────────────────┴───────────────────────────┐
                  ▼                                                       ▼
      [BigQuery Graph Datasets]                               [Multi-Channel Deliverables]
  - noble-beanbag-497411-m4                               - data/leads_feed.json
  - national_audits (all_state_records)                   - evidence/FORENSIC_CORRELATION_MATRIX.json
  - onedrive_forensics (onedrive_documents)               - reports/auto_leads/latest.json
  - forensic_layers (ppp_loans, fca_timeline)             - 288 CCTV Proximity Analysis
                  │
                  ▼
   [Automated Verification & 3-Location Backup Engine]
   1. GitHub (origin/main)
   2. Local PC C:\ (C:\Users\HP\OneDrive\Documents\OsintNeoAi\backups\repo\)
   3. Google Drive (Sharedall/OsintNeoAi/ via rclone gdrive:)
```

## Feature Inventory
Every requirement and discovered capability is indexed and assigned to a milestone.

| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Master Sheet Ingestion | Synchronize & parse all 40 worksheets of Google Sheet `1hKx1-8YnvrvAv9H6AQunli3dFSwsyIB3rF1yluO2Y1U` (live + offline cache fallback) | M1 | Survey R1 |
| 2 | Entity Registry Normalization | Normalize and validate entity IDs across `PER-###`, `GOV-###`, `CON-###`, `SHL-###`, `NP-###`, `EV-###`, `RICO-###`, `TOX-###`, `UP-###`, `ADDR-###`, `PHONE-###`, `EMAIL-###`, `LEG-###`, `TL-###`, `TRAF-###`, `FIN-###`, `FAC-###` | M1 | Survey R1 |
| 3 | USPS CASS Address & APN Standardizer | Canonicalize addresses per USPS Pub 28 (CASS expansion) and standard 8/10-digit Orange County APNs | M1 | Survey R1 |
| 4 | Multi-Format File Crawler & Archive Stream | Memory-bounded lazy streaming crawler handling PDFs, images, HTML, zips, tarballs in 64KB blocks | M2 | Survey R2 |
| 5 | Cryptographic SHA-256 Provenance | Continuous constant-memory streaming SHA-256 calculation and RFC 8785 Merkle tree root hash generation | M2 | Survey R2 |
| 6 | 5-Tier Extraction Ladder & Neural OCR | PyMuPDF digital text extraction, RapidOCR ONNX inference, and CLAHE image preprocessing fallbacks | M2 | Survey R2 |
| 7 | Audit-Ready Granular Transcripts | Structured JSON transcript persistence containing 2D bounding boxes, page coordinates, and confidence scores | M2 | Survey R2 |
| 8 | BigQuery Graph Dataset Ingestion | Load normalized entities, nodes, and relationship edges into BigQuery project `noble-beanbag-497411-m4` (`national_audits`, `onedrive_forensics`, `forensic_layers`, `npi_forensic`) | M3 | Survey R3 |
| 9 | Topological Graph Correlation & Lead Vectors | Traverse 104,000+ entity graph and extract 6 topological lead vectors (`PPP_PROPERTY_OVERLAP`, `MULTI_ORG_PERSON`, `ADDRESS_SHELL_CLUSTER`, `HIGH_RISK_PPP`, `LITIGATION_EXPOSURE`, `CHDO_STRAW_BUYER_NEXUS`) | M3 | Survey R3 |
| 10 | 288 Caltrans D12 CCTV Spatial Proximity | Geodesic Haversine spatial proximity computation between target anchor clusters and 288 CCTV feeds | M3 | Survey R3 |
| 11 | Multi-Channel Output Serialization | Generate `data/leads_feed.json`, `evidence/FORENSIC_CORRELATION_MATRIX.json`, and `reports/auto_leads/latest.json` | M3 | Survey R3 |
| 12 | 3-Location Backup Synchronization | Automated 3-location backup across GitHub (`origin/main`), Local PC C:\, and Google Drive (`Sharedall/OsintNeoAi/` via `rclone`) adhering to AGENTS.md rules | M4 | Survey R4 |
| 13 | 4-Tier & 5-Gate Automated Verification Suite | Comprehensive verification harness executing Tiers 1-4 (71 tests) + Tier 5 (Adversarial Coverage & Backup Verification) + 5-Gate Audit | M4 / E2E Track | Survey R4 |
| 14 | Final 100% E2E Acceptance & Adversarial Hardening | Verification of end-to-end execution across all 40 tabs, OCR files, BigQuery datasets, and backup sync | M5 / Final | Survey R1-R4 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Master Sheet Sync & Entity Normalizer | 40-tab parser, registry validators (`PER-`, `GOV-`, `CON-`, `SHL-`, `EV-`, `RICO-`, `TOX-`, `UP-`), CASS address/APN sanitizers, offline fallback | none | PLANNED |
| M2 | Neural OCR & Evidence Ingestion Engine | RapidOCR ONNX + PyMuPDF 5-tier extraction ladder, streaming archive reader, constant-memory SHA-256 hasher, 3NF SQLite vault, bounding box JSON generator | none | PLANNED |
| M3 | BigQuery Graph Mapping & Spatial Correlation | BigQuery schemas for `noble-beanbag-497411-m4`, 6 lead correlation vectors, 288 Caltrans CCTV geodesic solver, JSON feed generator | M1, M2 | PLANNED |
| M4 | 3-Location Backup & Verification Integration | Full 3-location synchronization engine (GitHub main, Local PC C:\, Google Drive Sharedall/OsintNeoAi/), manifest validation, invariant verification runners | M1, M2, M3 | PLANNED |
| M5 | Final E2E Test Pass & Adversarial Hardening | Execute 100% of E2E Test Suite (Tiers 1-4) published by E2E Testing Track, run Tier 5 white-box adversarial stress tests, verify zero data loss | M1, M2, M3, M4, TEST_READY | PLANNED |

## Interface Contracts

### Master Sheet Sync ↔ Graph & Entity Resolver
- Input: Google Sheet ID `1hKx1-8YnvrvAv9H6AQunli3dFSwsyIB3rF1yluO2Y1U` or cached CSVs in `master_osint_sheet/*.csv` / `evidence/google_drive/gsheet_1hKx1-8YnvrvAv9H6AQunli3dFSwsyIB3rF1yluO2Y1U.csv`
- Output Schema:
  ```json
  {
    "entity_id": "PER-001",
    "canonical_name": "JOHN DOE",
    "entity_type": "PERSON",
    "primary_tab": "People",
    "related_ids": ["GOV-001", "SHL-002"],
    "attributes": { "apn": "123-456-78", "address": "123 MAIN STREET, ANAHEIM, CA 92805" },
    "last_updated": "2026-09-02T00:00:00Z"
  }
  ```

### Neural OCR Ingestion ↔ SQLite Vault & Catalog Exporter
- Input: File path or byte stream (PDF, PNG, JPG, TIFF, ZIP, TAR)
- Output Schema:
  ```json
  {
    "file_id": "doc_01j6abc...",
    "sha256": "64-character-hex-hash",
    "filename": "exhibit_a.pdf",
    "extraction_tier": "tier2_neural_ocr",
    "page_count": 5,
    "pages": [
      {
        "page_number": 1,
        "text": "Extracted text content...",
        "avg_confidence": 0.962,
        "lines": [
          { "text": "Extracted line", "confidence": 0.98, "bbox": [10.0, 15.0, 200.0, 30.0] }
        ]
      }
    ],
    "entities_discovered": ["PER-001", "GOV-002", "18 U.S.C. § 1343"]
  }
  ```

### Correlation Engine ↔ BigQuery & Deliverables
- BigQuery Project: `noble-beanbag-497411-m4`
- Target Datasets: `national_audits`, `onedrive_forensics`, `forensic_layers`, `npi_forensic`
- Output JSON Files: `data/leads_feed.json`, `evidence/FORENSIC_CORRELATION_MATRIX.json`, `reports/auto_leads/latest.json`, `evidence/target_cctv_proximity.json`

### 3-Location Backup Protocol Contract
1. **Location 1 (GitHub)**: Remote `origin`, branch `main`.
2. **Location 2 (Local PC)**: `C:\Users\HP\OneDrive\Documents\OsintNeoAi\backups\repo\backup_YYYYMMDD_HHMMSS\`
3. **Location 3 (Google Drive)**: `gdrive:Sharedall/OsintNeoAi/backup_YYYYMMDD_HHMMSS/` via `rclone`

## Code Layout
- `master_osint_sheet/` — 40-tab CSV exports and documentation
- `workspaces/osintneoai_indexer/` — 5-tier neural OCR engine, streaming archive crawler, SQLite vault, RFC 8785 exporter
- `api/osint_pipeline/` — Entity normalizers, address sanitizers, APN formatters, pipeline runners
- `scripts/` — Correlation engines (`auto_leads_correlation_v2.py`), CCTV solvers, 3-location backup runners (`backup_repo_3way.py`), adversarial verification gates
- `tests/` — E2E test suites (Tiers 1-4), concurrency stress tests, official records tests
- `evidence/` — Primary evidence artifacts, OCR transcripts, correlation matrices, geojson files
- `reports/` — Daily investigative dossiers, automated lead briefings
