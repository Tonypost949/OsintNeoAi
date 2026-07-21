# OSINT & Takeout Ingestion Master Document: Walkthrough, Schemas, & File Paths

This document contains the complete operational record, BigQuery table summaries, SQL query guides, and local path to GitHub URL mappings for the OSINTNeoAi system.

---

## 1. Master Summary of Ingested Datasets

All records have been processed and loaded live into your BigQuery dataset `national_audits` under project **`project-743aab84-f9a5-4ec7-954`**:

| BigQuery Target Table | Content Description | Ingested Count | Data Volume | Status |
| :--- | :--- | :--- | :--- | :--- |
| **`national_audits.takeout_chrome_history`** | Chrome browsing history, search URLs, page titles, and timestamps | **1,340 records** | Full timeline | **LIVE** |
| **`national_audits.takeout_documents`** | Extracted text and tabular data from PDFs, CSVs, XLSX, JSON, Markdown, and TXT | **1,142 files** | **201.3 MB** | **LIVE** |

### Breakdown of Ingested Document & Spreadsheet Types (`national_audits.takeout_documents`)

* **Markdown Files (`.md`)**: 724 files (30.9 MB)
* **JSON Databases (`.json`)**: 197 databases (83.0 MB)
* **Text Documents (`.txt`)**: 168 files (59.7 MB)
* **CSV Spreadsheets (`.csv`)**: 42 spreadsheets (25.6 MB)
* **Excel Workbooks (`.xlsx`)**: 6 workbooks (262 KB)
* **PDF Documents (`.pdf`)**: 5 PDFs (1.6 MB)

---

## 2. Core Operational & Context File Paths

* **Resurrection Context Profile**: `C:\OsintNeoAi\agent\Antigravity_Resurrection_Protocol_makavali.md`
  * Raw GitHub URL: `https://github.com/Tonypost949/OsintNeoAi/blob/main/agent/Antigravity_Resurrection_Protocol_makavali.md`
* **Gemini Gem Persona Setup**: `C:\OsintNeoAi\agent\Gemini_Gem_Antigravity_makavali.md`
  * Raw GitHub URL: `https://github.com/Tonypost949/OsintNeoAi/blob/main/agent/Gemini_Gem_Antigravity_makavali.md`
* **Repository Paths CSV Sheet**: `C:\OsintNeoAi\repository_paths.csv`
  * Raw GitHub URL: `https://github.com/Tonypost949/OsintNeoAi/blob/main/repository_paths.csv`
* **Chrome Ingestion Pipeline**: `C:\OsintNeoAi\agent\ingest_takeout_pipeline.py`
  * Raw GitHub URL: `https://github.com/Tonypost949/OsintNeoAi/blob/main/agent/ingest_takeout_pipeline.py`
* **Document Ingestion Pipeline**: `C:\OsintNeoAi\agent\ingest_takeout_documents.py`
  * Raw GitHub URL: `https://github.com/Tonypost949/OsintNeoAi/blob/main/agent/ingest_takeout_documents.py`

---

## 3. Sample BigQuery SQL Queries

### Search Full Text across Ingested PDFs, Spreadsheets, and Documents
```sql
SELECT 
  file_name, 
  file_type, 
  row_count, 
  size_bytes, 
  SUBSTR(extracted_text, 1, 300) as preview 
FROM `project-743aab84-f9a5-4ec7-954.national_audits.takeout_documents`
WHERE LOWER(extracted_text) LIKE '%mercy house%' OR LOWER(extracted_text) LIKE '%orange county%'
ORDER BY size_bytes DESC;
```

### Search Chrome History Timeline
```sql
SELECT visit_time, title, url 
FROM `project-743aab84-f9a5-4ec7-954.national_audits.takeout_chrome_history`
ORDER BY visit_time DESC
LIMIT 20;
```

---

## 4. Key Local Paths & Raw GitHub URLs (Sample List)

For the complete catalog of **2,733 files**, refer directly to `C:\OsintNeoAi\repository_paths.csv`. Here is an excerpt:

```csv
Local Path,GitHub URL
C:\OsintNeoAi\.dockerignore,https://github.com/Tonypost949/OsintNeoAi/blob/main/.dockerignore
C:\OsintNeoAi\.env.example,https://github.com/Tonypost949/OsintNeoAi/blob/main/.env.example
C:\OsintNeoAi\.gitignore,https://github.com/Tonypost949/OsintNeoAi/blob/main/.gitignore
C:\OsintNeoAi\AGENTS.md,https://github.com/Tonypost949/OsintNeoAi/blob/main/AGENTS.md
C:\OsintNeoAi\alerts_flagged.json,https://github.com/Tonypost949/OsintNeoAi/blob/main/alerts_flagged.json
C:\OsintNeoAi\bookmarks_investigation_findings.md,https://github.com/Tonypost949/OsintNeoAi/blob/main/bookmarks_investigation_findings.md
C:\OsintNeoAi\briefings_data.js,https://github.com/Tonypost949/OsintNeoAi/blob/main/briefings_data.js
C:\OsintNeoAi\business_workbook.xlsx,https://github.com/Tonypost949/OsintNeoAi/blob/main/business_workbook.xlsx
C:\OsintNeoAi\capabilities_dashboard.html,https://github.com/Tonypost949/OsintNeoAi/blob/main/capabilities_dashboard.html
C:\OsintNeoAi\chokepoint_extraction_report.md,https://github.com/Tonypost949/OsintNeoAi/blob/main/chokepoint_extraction_report.md
C:\OsintNeoAi\chrome_bookmarks_dump.json,https://github.com/Tonypost949/OsintNeoAi/blob/main/chrome_bookmarks_dump.json
C:\OsintNeoAi\clock.html,https://github.com/Tonypost949/OsintNeoAi/blob/main/clock.html
C:\OsintNeoAi\cloudbuild.yaml,https://github.com/Tonypost949/OsintNeoAi/blob/main/cloudbuild.yaml
C:\OsintNeoAi\cloudflare-tunnel.sh,https://github.com/Tonypost949/OsintNeoAi/blob/main/cloudflare-tunnel.sh
```
