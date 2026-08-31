# OsintNeoAi Indexer — Comprehensive Survey & Investigation Report (R1 Analysis)

**Author:** Explorer Survey Agent (`explorer_survey_1`)  
**Date:** 2026-08-29  
**Target Workspace:** `C:\OsintNeoAi\workspaces\osintneoai_indexer`  
**Repository Working Directory:** `C:\OsintNeoAi`  

---

## 1. Executive Summary & Problem Boundary

The objective of the OsintNeoAi Indexer project is to build an automated document processing, OCR extraction, entity resolution, and timeline reconciliation pipeline to ingest, extract, and index records, financial transactions, and communications across local archives and external Google Drive links.

This survey investigation thoroughly audited:
1. **Local Input Archive Paths**: `C:\Users\Amd949609\Downloads` and `C:\OsintNeoAi\evidence`, detailing directory trees, file formats, size distributions, and high-value evidentiary items.
2. **Existing Repo Scripts & Assets**: Analyzed tools, OCR pipelines, and utilities across `C:\OsintNeoAi\agent\`, `C:\OsintNeoAi\core\AG2OSINTNEOMAXX\`, and `C:\OsintNeoAi\forensic\`.
3. **Python Runtime & Package Availability**: Audited the Python 3.14.7 environment, verified package importability and runtime execution for `pymupdf` (1.28.2), `pypdf` (6.16.2), `rapidocr-onnxruntime` (1.2.3), `pillow` (12.3.0), `python-docx` (1.2.0), `openpyxl` (3.1.5), `lxml` (6.1.1), `mailbox`, `email`, `sqlite3`, and `pytest` (9.1.1).
4. **Multi-Source Ingestion & Stream Handling Architecture (R1)**: Formulated an end-to-end memory-safe streaming and chunking architecture capable of handling multi-gigabyte archives, multi-page high-resolution TIFF/PDF scans, mailbox files, and external Google Drive references without unhandled exceptions or memory faults.

---

## 2. Local Input Archive Paths & File Inventory

### 2.1 Overview Comparison

| Metric | `C:\OsintNeoAi\evidence` | `C:\Users\Amd949609\Downloads` (Evidentiary Subset) |
|---|---|---|
| **Total Files** | 2,149 files | 283 evidentiary target files (out of 2,578 total files) |
| **Total Size** | 384.46 MB | ~2,476 MB (including evidentiary zips, medical records, and PDFs) |
| **Subdirectories** | 23 subdirectories | 8 subdirectories |
| **Primary Media** | 936 JPGs (Google Photos batches), 19 PDFs, 13 PNGs, 12 DOCX, 1088 TXT/transcripts, 1 ZIP | 48 PDFs, 51 HTMLs, 12 TIFs, 13 JPGs, 94 PNGs, 3 DOCX, 8 CSVs, 7 JSONs, 28 ZIPs |

---

### 2.2 Deep Dive: `C:\OsintNeoAi\evidence`

`C:\OsintNeoAi\evidence` is the primary curated repository of investigative case materials, court records, and intelligence logs.

#### Subdirectory Layout:
- `official_court_records/` (11 markdown transcripts and master index):
  - `01_USA_v_Harry_Sidhu_8_23_cr_00108_CJC.md` (Plea agreement, 4-count Information, FBI affidavit).
  - `02_HCD_Notice_of_Violation_Surplus_Land_Act.md` ($96M penalty analysis).
  - `03_USA_v_Todd_Ament_and_Melahat_Rafiei.md` (Guilty pleas, wire fraud).
  - `04_OC_Superior_Court_Case_30_2021_01201327_Full_ROA.md` (61-entry Register of Actions).
  - `04_USA_v_Christopher_Ryan_3_20_mj_05007_TJB.md` (Federal magistrate complaint).
  - `05_Woodbridge_Meadows_v_Dimarcello_30_2021_01201327_CL_UD_CJC.md` (38.5 KB court docket & triple default record).
  - `06_JL_Investigation_Anaheim_Forensic_Audit_Report.md` (Chamber of Commerce slush fund audit).
  - `07_Anaheim_City_Council_Stadium_Voidance_Resolution_2022_064.md` (Voiding $320M stadium sale).
  - `08_Multi_State_Police_and_Commercial_Incident_Logs.md` (Hamilton NJ, Ewing NJ, Quantum Auto Dismantler logs).
  - `OFFICIAL_DOCUMENTS_INDEX.md` (Master catalog).
- `google_photos_evidence/` through `google_photos_evidence_batch8/`:
  - 936 high-resolution JPEG photos (326.20 MB total) spanning photos 001 to 120 across 8 batches.
  - Documenting physical site inspections, eviction notices, hazardous conditions, and evidence photos.
- `ocr_transcripts_photos/`:
  - 885 pre-computed `.jpg.txt` OCR transcripts matching photo items.
- `google_drive/` (50 files):
  - 12 Google Docs exports (`.docx` / `.txt` pairs) including `DR_ANN_VERMA_RESCISSION_NOTICE.docx`, `gdoc_1aiK_*.docx`, `gdoc_1dqmhxx*.docx` (2.89 MB – 3.08 MB each).
  - 12 `.bin` raw downloads (`gfile_*.bin` up to 8.17 MB).
  - 7 Google Sheets exports (`gsheet_*.csv`).
  - Environmental PDFs (`BUCK_RANCH_CALLENS_RANCH_GIS_ANALYSIS.pdf`, `INDIAN_BURIAL_SEARCH_REPORT_1.pdf`, `SOIL_ANALYSIS_BURIAL_GROUND_VERIFICATION.pdf`).
  - `GDRIVE_INGESTION_MANIFEST.json`.
- `lawsuit_info_full_dimarcello/` (21 files, 1 zip):
  - Historical engineering blueprints, easement agreements (`1963-04-15 engineer yamada.pdf`, `1964-06-01 yamada.pdf`, `2015-08-04 - Easement Yamada Family Trust.pdf`).
  - State audit reports (`2017-112 homeless report.pdf`, `2018 state audit response homeless oc la.pdf`, `2021 dec phase 1 epa.pdf`).
  - Permit archive `17612 beach permits.Zip` (2.20 MB).
- `dns/`, `whois/`, `ssl/`, `http_headers/`, `endpoint_captures/`, `port_scans/`:
  - 1080+ network intelligence `.txt` files covering domains, certificate chains, and endpoint scans.
- `visualizations/`:
  - 6 HTML interactive diagrams (`timeline.html`, `rico_flow.html`, `cluster_map.html`, `risk_matrix.html`, `geo_map.html`, `port_heatmap.html`).

---

### 2.3 Deep Dive: `C:\Users\Amd949609\Downloads`

The Downloads folder contains recent primary evidentiary intakes, medical records, court search exports, invoices, and multi-page scanned TIFF files.

#### High-Value Evidentiary Categories in Downloads:
1. **Medical Records & Hospital Filings (TIFFs & PDFs)**:
   - `CONSENT SURGERY OR SPECIAL PROCEDURES.TIF` (16.51 MB, multi-page scanned record).
   - `CONSENT SURGERY OR SPECIAL PROCEDURES (1).TIF` (4.4 MB).
   - `Hospital Conditions of Admission (1).TIF` (0.34 MB), `General Consent for Treatment.TIF` (0.15 MB, 3 pages).
   - `Authorization for Release of Information.TIF` (0.24 MB), `Authorization to Release Protected Health Information.TIF` (0.22 MB).
   - `ED AVS Dec 14, 2025.PDF` (1.08 MB), `Itemized Bill_20260820.PDF`, `Patient Signature Dec 14, 2025.PDF`.
   - `medrec5444.pdf`, `rec1.pdf` through `rec66666.pdf`, `Sub 01 Sanderson.pdf`.
2. **Court Search Results & Legislative / Municipal Documents**:
   - `The Superior Court of California - Name Search Results.html` (along with subfolder files).
   - `Knabb_v__City_of_Huntington_Beach.pdf`.
   - `Anaheim Stadium Reddit Response.pdf`.
   - `Terms & Conditions 'A' - ED Treatment.HTML`, `Terms & Conditions 'B' - ED Financial.HTML`, `Chaperone Policy.HTML`.
   - `MyChart - Billing Account Details.html` (0.84 MB), `MyChart - Note from Care Team.html` (0.86 MB).
3. **Whistleblower Dossiers & Visual Intelligence**:
   - `Whistleblower_Audit_and_Forensic_Dossier.png` (4.03 MB).
   - `NotebookLM Mind Map (1).png` (0.79 MB), `NotebookLM Mind Map.png` (0.15 MB).
   - `Photo ID Card.JPG`, `Discharge Instruction.JPG`, `IMG_0427.JPG` – `IMG_0429.JPG` (2.8 MB – 3.54 MB each).
4. **Financial, Invoicing & Company Search Data**:
   - `Syncfusion_Invoice_W753756.pdf`, `Order Syncfusion® Products _ Receipt.pdf`, `Microsoft account _ Order history.pdf`.
   - `CompanySearch_mercyhouse_08272026_043835.csv`, `gmail_report_audit_2021_2026.csv`, `osint-query-results.csv`.
5. **Compressed Archives (.zip)**:
   - `HealthSummary_Aug_17_2026.zip`, `HealthSummary_Aug_28_2026 (1).zip`, `HealthSummary_Aug_29_2026 (2,3,4).zip` (containing patient health summaries, XML/JSON exports).
   - `drive-download-20260817T084645Z-1-001.zip`, `drive-download-20260817T084709Z-1-001.zip`.
   - `Photos.zip`, `Photos (1,2,3).zip` (6 MB – 11 MB each).

---

## 3. Existing Repository Assets & Reusable Patterns

The repository contains battle-tested extraction, parsing, and correlation code that can be directly leveraged:

### 3.1 OCR & Text Extraction Engine
- **`agent/batch_photos_evidence_ocr.py` & `agent/batch_photos_album2_ocr.py`**:
  - Structured 7-point forensic extraction schema (Category, Document Title/Form Type, Case/Record Number, Court/Agency/Jurisdiction, Named Entities, Dates/Timestamps, Key Evidence Transcript & Factual Summary).
  - Robust batching and incremental checkpointing via `id` keys in manifest files.
- **`agent/_extract_text_content.py`**:
  - Implements MIME-type dispatching (`text/*`, `application/pdf`, `application/vnd.openxmlformats-officedocument...`).
  - PyMuPDF (`fitz` / `pymupdf`) stream loading (`doc = pymupdf.open(stream=data, filetype="pdf")`).
- **`agent/azure_ocr_permits.py`**:
  - Multi-page image and PDF rasterization pipelines.

### 3.2 Takeout, Mailbox & Stream Ingestion
- **`agent/ingest_takeout_mail.py`**:
  - Uses standard library `mailbox.mbox` to process mailbox archives.
  - MIME header decoding (`email.header.decode_header`) handling multi-charset headers (`utf-8`, `iso-8859-1`, `windows-1252`).
  - Multi-pattern email timestamp parser (`parse_date`).
- **`agent/ingest_takeout_chunks.py`**:
  - Demonstrates streamed unzipping of large Google Takeout archives without full disk extraction.

### 3.3 Entity Extraction & Relationship Linking
- **`agent/entity_extractor.py`**:
  - Regex engines for:
    - **Names**: `\b([A-Z][a-z]{1,20}\s+(?:[A-Z]\.?\s+)?[A-Z][a-z]{1,20}(?:\s+(?:Jr|Sr|III|II|IV)\.?)?)\b`
    - **Addresses**: Full street patterns with suffixes (`St|Street|Ave|Blvd|Dr|Ln|Rd|Way|Ct|Pl|Cir`) and suite/unit identifiers.
    - **Financial Amounts**: `\$[\d,]+(?:\.\d{1,2})?(?:\s*(?:million|billion|M|B|K))?`
    - **Federal/State Case Numbers**: `\b\d{1,2}:\d{2}-(?:cv|cr|mc|mj|ml)-\d{3,6}(?:-[A-Z]{2,5}(?:-[A-Z]{2,5})?)?\b` and state format `30-2021-01201327-CL-UD-CJC`.
    - **Organizations**: Standard corporate and municipal identifiers (`Inc|LLC|Corp|Foundation|Association|Group|Solutions|Center|Institute|LLP|LP|Ltd`).
    - **Smoking Gun Keywords**: 30+ legal, corruption, and environmental terms (`indictment`, `guilty plea`, `wire fraud`, `restitution`, `rico`, `qui tam`, `false claims`, `unsealed`, `hexavalent chromium`, `ceqa`, `superfund`).
- **`core/AG2OSINTNEOMAXX/onedrive_ingestion_engine.py`**:
  - Canonical indexing, SHA-256 calculation, and duplicate avoidance.
- **`forensic/generate_all_deliverables.py`**:
  - Definitive ground-truth schema for `RICO_NODES` (`RICO-001` to `RICO-005`), `PEOPLE` (`PER-001` to `PER-010`), `GOV_AGENCIES` (`GOV-001` to `GOV-003`), `EVIDENCE_ITEMS` (`EV-001` to `EV-005`), and `LEGAL_EXPOSURE` (`18 U.S.C. § 1962(c)`, `31 U.S.C. § 3730(h)`, `Cal. Labor Code § 1102.5`).

---

## 4. Python Runtime & Available Packages Audit

An exhaustive import and execution probe was conducted on the active Python runtime (`Python 3.14.7 64-bit`, located at `C:\Users\Amd949609\AppData\Local\Python\pythoncore-3.14-64\python.exe`):

### 4.1 Package Status Matrix

| Package / Module | Version | Status | Pipeline Role & Suitability |
|---|---|---|---|
| `pymupdf` (`fitz`) | 1.28.2 | **Installed & Verified** | Primary PDF text extraction, page rendering to pixmap, image extraction. Fast and memory-efficient. |
| `pypdf` | 6.16.2 | **Installed & Verified** | Secondary PDF reader, metadata extraction, page stream handling. |
| `rapidocr-onnxruntime` | 1.2.3 | **Installed & Verified** | High-accuracy neural OCR running on ONNX runtime. Completely offline, 0 external binaries required. Verified working directly in Python 3.14! |
| `onnxruntime` | 1.29.0 | **Installed & Verified** | High-performance inference engine powering RapidOCR. |
| `opencv-python` | 5.0.0.93 | **Installed & Verified** | Image preprocessing, thresholding, deskewing for OCR. |
| `pillow` (`PIL`) | 12.3.0 | **Installed & Verified** | Multi-page TIFF iteration (`ImageSequence`), JPEG/PNG processing, format normalization. |
| `python-docx` | 1.2.0 | **Installed & Verified** | Word document (`.docx`) paragraph, table, and header text extraction. |
| `openpyxl` | 3.1.5 | **Installed & Verified** | Excel (`.xlsx`) sheet row streaming. |
| `lxml` | 6.1.1 | **Installed & Verified** | Ultra-fast HTML/XML parsing and entity stripping. |
| `html.parser` | Stdlib | **Installed & Verified** | Pure Python HTML tag cleaner and text extractor. |
| `mailbox` | Stdlib | **Installed & Verified** | `.mbox` file streaming and message iteration. |
| `email` | Stdlib | **Installed & Verified** | `.eml` / RFC822 MIME message decoding, attachment extraction. |
| `sqlite3` | Stdlib | **Installed & Verified** | Relational vault storage (`timeline_vault.db`), indexing, full-text search (FTS5). |
| `hashlib` | Stdlib | **Installed & Verified** | SHA-256 chunked cryptographic hashing. |
| `pytest` | 9.1.1 | **Installed & Verified** | Automated test suite execution for R4 invariant verification. |
| `google.cloud.bigquery` | 3.43.0 | **Installed & Verified** | BigQuery integration if cloud export is activated. |
| `google.cloud.vision` | 3.15.0 | **Installed & Verified** | Cloud Vision OCR fallback. |
| `pydantic` | 2.13.4 | **Installed & Verified** | Schema validation and model serialization. |
| `tqdm` | 4.70.0 | **Installed & Verified** | Progress bar logging for batch ingestion runs. |
| `chardet` | 5.2.0 | **Installed & Verified** | Character encoding autodetection for legacy documents. |
| `python-dateutil` | 2.9.0.post0 | **Installed & Verified** | Fuzzy timestamp parsing and ISO 8601 normalization. |

### 4.2 Handling Missing / Uninstalled Modules
- **`bs4` (BeautifulSoup4)**: Not installed.  
  *Solution:* Use `lxml` or standard library `html.parser.HTMLParser`, which was verified in sanity tests to extract clean document text from complex HTML files (e.g. MyChart, Chaperone Policy) in milliseconds.
- **`pdfplumber` / `pdfminer`**: Not installed.  
  *Solution:* `pymupdf` (1.28.2) is already installed, orders of magnitude faster, and handles both native digital text and image pixmap rendering.
- **`pytesseract` / `easyocr`**: Not installed.  
  *Solution:* `rapidocr-onnxruntime` (1.2.3) is fully functional and requires no external Tesseract OCR binary installation or heavy PyTorch downloads.

---

## 5. R1 Architecture: Multi-Source Ingestion & Stream Handling

To satisfy Requirement R1 ("Ingest PDFs, images, HTML documents, and mailbox files from local directories and external Google Drive links. The ingestion engine must use streaming/chunking to handle large archives without memory overflow"), the ingestion subsystem must follow a strict stream-oriented architectural design.

```
+----------------------------------------------------------------------------------------------------+
|                                     INGESTION STREAM GENERATOR                                      |
+----------------------------------------------------------------------------------------------------+
|  [Evidence Dir]        [Downloads Dir]          [Google Drive / Manifests]      [Nested Archives]   |
|   2,149 files            283 doc/media            50+ files / Links              29 .zip files      |
+----------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+----------------------------------------------------------------------------------------------------+
|                                 STREAM CHUNKING & HASHING ENGINE                                   |
| - 64 KB Block-by-Block SHA-256 Digesting (Hash before memory load)                                |
| - Deduplication Filter against SQLite Index Registry                                               |
+----------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+----------------------------------------------------------------------------------------------------+
|                                    FORMAT-SPECIFIC STREAM PARSERS                                  |
| +-------------------------+ +-------------------------+ +-------------------------+ +------------+ |
| | PDF Stream Parser       | | Image/TIFF Streamer     | | HTML Stream Cleaner     | | Mail Parser| |
| | - Page-by-page iterator | | - Multi-page frame iter | | - Stream tokenizer      | | - Mbox gen | |
| | - Native text extract   | | - RapidOCR neural engine| | - Script/style strip    | | - EML MIME | |
| | - Pixmap OCR on scan    | | - Auto-downsampling     | | - Entities & text       | | - Attach   | |
| +-------------------------+ +-------------------------+ +-------------------------+ +------------+ |
+----------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+----------------------------------------------------------------------------------------------------+
|                            ENTITY RESOLUTION & TIMELINE NORMALIZER                                 |
| - Regex & Heuristic Extraction: Names, Addresses, Dollar Amounts, Case #s, Agencies, Keywords     |
| - ISO 8601 Timestamp Normalization (`YYYY-MM-DD` / `YYYY-MM-DDTHH:MM:SSZ`)                         |
+----------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+----------------------------------------------------------------------------------------------------+
|                                 BATCHED SINK PERSISTENCE LAYER                                     |
| +---------------------------------------------------+ +------------------------------------------+ |
| | SQLite Database: timeline_vault.db                | | Master Catalog:                          | |
| | - WAL mode, 250-record transaction chunks         | |   master_timeline_catalog.json           | |
| | - FTS5 Full-Text Search Virtual Tables            | | - Streaming JSON Array Export            | |
| +---------------------------------------------------+ +------------------------------------------+ |
+----------------------------------------------------------------------------------------------------+
```

---

### 5.1 Streaming Ingestion Mechanics

1. **Lazy File Generator**:
   - Never load file lists or binary content into giant in-memory lists.
   - Implement `yield` generators traversing `C:\OsintNeoAi\evidence` and `C:\Users\Amd949609\Downloads`.
   - Exclude high-entropy irrelevant binaries (`.pyc`, `.dll`, `.exe`, `.jar`, `.rpyc`, `.download`).

2. **Chunked Cryptographic Hashing**:
   - Compute SHA-256 in 64 KB binary blocks:
     ```python
     def compute_sha256_stream(filepath, chunk_size=65536):
         h = hashlib.sha256()
         with open(filepath, 'rb') as f:
             while chunk := f.read(chunk_size):
                 h.update(chunk)
         return h.hexdigest()
     ```
   - Enables constant memory usage ($O(1)$ RAM) regardless of file size (e.g. 1.7 GB Swift installer or 760 MB game zip).

3. **Page-by-Page PDF Streaming**:
   - Open PDF with `pymupdf.open(filepath)`.
   - Iterate pages sequentially:
     - Check `page.get_text()`. If length > 50 characters, record native text directly.
     - If page has 0 characters (scanned image page), render pixmap at 150 DPI (`page.get_pixmap(dpi=150)`), pass NumPy array to `RapidOCR()`, and discard pixmap memory immediately.
     - Close document handle `doc.close()`.

4. **Multi-Page TIFF & Image Frame Streaming**:
   - Open `.tif` via `PIL.Image.open(filepath)`.
   - Iterate frames using `ImageSequence.Iterator(im)`:
     - Convert frame to RGB NumPy array.
     - Run `RapidOCR()` per frame.
     - Close image handle.

5. **In-Memory Zip Archive Streaming**:
   - Open zip archives with `zipfile.ZipFile(filepath, 'r')`.
   - Iterate `z.infolist()`. For entries matching document extensions (`.pdf`, `.html`, `.txt`, `.xml`, `.eml`), stream bytes directly via `z.open(entry)` into format parsers without writing temporary files to disk.

6. **Mailbox & EML Message Streaming**:
   - For `.mbox` files, iterate via `mailbox.mbox(mbox_path)` generator.
   - For `.eml` / `.msg` files, use `email.message_from_bytes()`.
   - Extract headers (`From`, `To`, `Date`, `Subject`, `Message-ID`), decode MIME parts, parse RFC822 dates to ISO 8601, and stream body text.

---

### 5.2 Target Data Model & Relational Schema (`timeline_vault.db`)

The relational database `timeline_vault.db` must feature the following normalized schema:

#### Table: `documents`
- `id` (TEXT PRIMARY KEY) — Canonical unique ID (e.g. `DOC-xxxxxxxxxxxx`)
- `sha256` (TEXT UNIQUE NOT NULL) — Cryptographic SHA-256 hash
- `source_path` (TEXT NOT NULL) — Source path or URI
- `source_origin` (TEXT NOT NULL) — `evidence`, `downloads`, `gdrive`, `zip`
- `file_type` (TEXT NOT NULL) — `pdf`, `image`, `html`, `docx`, `email`, `text`, `csv`, `json`
- `file_size_bytes` (INTEGER NOT NULL)
- `doc_date` (TEXT) — Normalized ISO 8601 date (`YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SSZ`)
- `title` (TEXT) — Extracted title or subject
- `sender` (TEXT) — Author / Sending party
- `recipient` (TEXT) — Recipient / Target agency
- `case_number` (TEXT) — Detected federal or state case number
- `financial_amount` (REAL) — Primary extracted dollar amount (if present)
- `text_body` (TEXT NOT NULL) — Full extracted / OCR text
- `ocr_applied` (INTEGER NOT NULL) — 1 if OCR was executed, 0 if digital text
- `ingested_at` (TEXT NOT NULL) — Pipeline ingestion ISO timestamp

#### Table: `entities`
- `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
- `doc_id` (TEXT NOT NULL, FOREIGN KEY -> `documents.id`)
- `entity_type` (TEXT NOT NULL) — `PERSON`, `ORGANIZATION`, `ADDRESS`, `CASE_NUMBER`, `DOLLAR_AMOUNT`, `KEYWORD`
- `entity_value` (TEXT NOT NULL)
- `normalized_value` (TEXT NOT NULL)

#### Table: `timeline_events`
- `event_id` (TEXT PRIMARY KEY) — `EVT-xxxxxxxxxxxx`
- `doc_id` (TEXT NOT NULL, FOREIGN KEY -> `documents.id`)
- `event_date` (TEXT NOT NULL) — ISO 8601 date for chronological sorting
- `actor` (TEXT)
- `action_summary` (TEXT NOT NULL)
- `legal_significance` (TEXT)

#### Table: `documents_fts` (Virtual FTS5 Table)
- Full-text search index over `(doc_id UNINDEXED, title, sender, recipient, case_number, text_body)`.

---

## 6. Recommendations & Implementation Blueprint

For subsequent pipeline implementation agents:
1. **Target Working Directory**: Build the pipeline in `C:\OsintNeoAi\workspaces\osintneoai_indexer\`.
2. **Reuse Existing Fast OCR**: Instantiate `RapidOCR()` once per process and reuse across all images/scans.
3. **Use Pre-computed Transcripts where Verified**: 885 transcripts in `evidence/ocr_transcripts_photos/` and `evidence/lawsuit_info_full_dimarcello/ocr_transcripts/` can be indexed directly, saving hours of redundant neural inference while remaining verifiable against source SHA-256 hashes.
4. **Automated Invariant Test Suite (`tests/test_indexer_invariants.py`)**:
   - `test_sha256_uniqueness_and_integrity`: Asserts every record in `timeline_vault.db` and `master_timeline_catalog.json` matches the on-disk SHA-256 hash of its source.
   - `test_iso8601_date_normalization`: Asserts 100% of non-null dates conform to `^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)?$`.
   - `test_chronological_ordering`: Asserts master timeline entries are strictly monotonic chronologically.
   - `test_entity_relational_consistency`: Asserts 100% of foreign keys in `entities` resolve to valid records in `documents`.
