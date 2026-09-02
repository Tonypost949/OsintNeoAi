# E2E Test Infra: OsintNeoAi Full-Cycle Pipeline

## Test Philosophy
- Opaque-box, requirement-driven. Derived from `ORIGINAL_REQUEST.md` specifications.
- Methodology: Category-Partition + Boundary Value Analysis + Pairwise Combinatorial + Real-World Workload Testing.

## Feature Inventory
| # | Feature | Source (requirement) | Tier 1 (Feature) | Tier 2 (Boundary) | Tier 3 (Cross) | Tier 4 (Real-World) |
|---|---------|---------------------|:----------------:|:-----------------:|:--------------:|:-------------------:|
| 1 | Multi-Format Evidence Ingestion | ORIGINAL_REQUEST §R1 | 5 | 5 | ✓ | ✓ |
| 2 | Neural & Fallback OCR Processing | ORIGINAL_REQUEST §R1 | 5 | 5 | ✓ | ✓ |
| 3 | Cryptographic SHA-256 Manifest | ORIGINAL_REQUEST §R1 | 5 | 5 | ✓ | ✓ |
| 4 | Named Entity Resolution | ORIGINAL_REQUEST §R2 | 5 | 5 | ✓ | ✓ |
| 5 | BigQuery Graph Schema Mapping | ORIGINAL_REQUEST §R2 | 5 | 5 | ✓ | ✓ |
| 6 | Daily Intelligence Dossier Gen | ORIGINAL_REQUEST §R3 | 5 | 5 | ✓ | ✓ |
| 7 | Chronological Event Timeline | ORIGINAL_REQUEST §R3 | 5 | 5 | ✓ | ✓ |
| 8 | Cross-Entity Correlation Matrix | ORIGINAL_REQUEST §R3 | 5 | 5 | ✓ | ✓ |
| 9 | Autonomous Full-Cycle Runner | ORIGINAL_REQUEST §R1-R3 | 5 | 5 | ✓ | ✓ |
| 10| 3-Location Backup Protocol | ORIGINAL_REQUEST §R4 | 5 | 5 | ✓ | ✓ |

## Test Architecture
- Test runners: `python -m unittest tests/test_osint_forensic_pipeline.py` and `python test_pipeline.py`
- Test case format: Automated unit and integration assertions covering inputs, schemas, SHA-256 hashes, graph topologies, report formats, and backup triggers.
- Test directory: `tests/test_osint_forensic_pipeline.py` and project root `test_pipeline.py`.

## Real-World Application Scenarios (Tier 4)
| # | Scenario | Features Exercised | Complexity |
|---|----------|--------------------|------------|
| 1 | Ingest raw court filings + medical PDFs, run OCR, extract entities, format BigQuery tables | F1, F2, F3, F4, F5 | High |
| 2 | Ingest mixed zip archive with images & text, generate daily intelligence dossier in reports/daily/ | F1, F2, F6, F7, F8 | High |
| 3 | End-to-end full cycle execution from raw directory to reports and 3-location backup verification | F1-F10 | High |
| 4 | Graph correlation across multi-agency entities and APN property records into BigQuery schema | F4, F5, F8 | Medium |
| 5 | Integrity verification of SHA-256 hashes, timestamps, and non-degradation of prior records | F3, F9, F10 | Medium |

## Coverage Thresholds
- Tier 1: ≥5 per feature
- Tier 2: ≥5 per feature (where boundaries exist)
- Tier 3: Pairwise coverage of major feature interactions
- Tier 4: ≥5 realistic application scenarios
- Tier 5: Adversarial edge cases & fuzzing
