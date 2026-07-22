---
name: deep-osint
description: Executes forensic local scanning (with OCR), Google Drive/Gmail OSINT queries, timeline parsing from Takeout location/photo files, Maltego entity mapping, and references professional municipal investigation dossiers.
---

# Deep OSINT Investigation Skill Guide

You are equipped with the **Deep OSINT Skill**, a professional-grade intelligence collection, analysis, and mapping suite. This guide instructs you on how to leverage the included tools and evidence databases to execute deep investigatory tasks.

---

## 8-Phase Deep OSINT Framework

When tasked with an investigation, apply the following 8-phase framework:
1. **Target Classification & Jurisdiction**: Map target entities (individuals/companies) to legal venues.
2. **Local Forensic Scanner (OCR)**: Recursively index local files, hashes, and text without modifications.
3. **Google Drive & Gmail Audits**: Authenticate via APIs to index daily activities, documents, and communications.
4. **Google Dorking Generation**: Produce public Drive, Sheets, and Forms dork links for OSINT discovery.
5. **Timeline Parsing**: Parse location history, photo EXIF files, and build synchronized master timelines.
6. **Maltego Entity Mapping**: Translate raw intelligence into structured Maltego XML entities (Person, Location, Org).
7. **Secure Database Terminal**: Query structured national audits/discrepancies databases via BigQuery.
8. **Dossier & Relationship Reporting**: Compile Intelligence Dossiers, Legal-Grade Evidence Packages, and Relationship Matrices.

---

## Tool Command Reference

Use the following python tools located in the skill's `scripts/` directory:

### 1. Local Forensic Scanner (`core_scanner.py`)
Scans folders recursively, hashes files (SHA256), extracts email/phones/numbers, and runs optional Tesseract OCR on images.
- **Run command**:
  ```powershell
  python "{SKILL_DIR}/scripts/core_scanner.py" --root "C:\Path\To\Scan" --outdir "C:\Path\To\Outputs" [--ocr]
  ```
- **Outputs**:
  - `osint_YYYYMMDDTHHMMSSZ.xlsx` (contains FileInventory, ExtractedTextIndex, Emails, Phones, Numbers, Matches sheets)
  - `dl_file_index_YYYYMMDDTHHMMSSZ.csv`

### 2. Google Drive & Gmail daily search dashboard (`search_drive.py`)
A comprehensive authenticated search dorker and localized timeline server.
- **Start Web Dashboard (Interactive UI on Port 8080)**:
  ```powershell
  python "{SKILL_DIR}/scripts/search_drive.py" --serve
  ```
- **Authenticate Client**:
  ```powershell
  python "{SKILL_DIR}/scripts/search_drive.py" --auth
  ```
- **Run API Query**:
  ```powershell
  python "{SKILL_DIR}/scripts/search_drive.py" --query "Target Name"
  ```
- **Generate Dorks**:
  ```powershell
  python "{SKILL_DIR}/scripts/search_drive.py" --dork "Target Name"
  ```

### 3. Timeline/Takeout Parsers (`build_timeline.py`)
Builds master timelines from raw files like Google Takeout Location History and Photo EXIF metadata.
- **Parse location history JSON**:
  ```powershell
  python "{SKILL_DIR}/scripts/parse_location_history.py" --input "path/to/LocationHistory.json" --output "path/to/parsed_location.csv"
  ```
- **Parse Google Photo metadata JSONs**:
  ```powershell
  python "{SKILL_DIR}/scripts/parse_photos_metadata.py" --input "path/to/takeout/photos/" --output "path/to/parsed_photos.csv"
  ```
- **Build Master Timeline (.ics & .html)**:
  ```powershell
  python "{SKILL_DIR}/scripts/build_timeline.py" --locations "parsed_location.csv" --photos "parsed_photos.csv" --outdir "timeline_output"
  ```

### 4. Maltego Local Transform (`gemini_osint_transform.py`)
Uses `gemini-2.0-flash` to structure unstructured text into Maltego Person, Organization, and Location entities.
- **Execution**:
  ```powershell
  python "{SKILL_DIR}/scripts/gemini_osint_transform.py" "Raw unstructured data text here"
  ```

### 5. Streamlit BQ Terminal (`app.py`)
Runs Streamlit terminal that securely queries BigQuery state-wide audit tables for target matches.
- **Run command**:
  ```powershell
  streamlit run "{SKILL_DIR}/scripts/app.py"
  ```

---

## Case Study References

Refer to case study folders under the `references/` directory for legal-grade evidence compilation models and investigation techniques:
- `chi_gates_dossier.md` — Complete 8-phase dossier reporting format.
- `craig_steele_analysis.txt` — Analysis of two-track investigations (legal vs cyber-surveillance).
- `navigation_center_financial_thread.txt` — Tracking discrepancies in public contracts (e.g., Mercy House contract gap).
- `anonymized_evidence.md` & `named_evidence.md` — Mappings for evidence tiers (A-D) and chain-of-custody.
