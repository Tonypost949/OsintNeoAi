---
name: osint-forensic-pipeline
description: >-
  Full-cycle OSINT forensic evidence pipeline for OsintNeoAi. Orchestrates
  evidence ingestion from Google Photos/Drive/OneDrive, bulk neural OCR,
  entity cross-referencing against BigQuery graph, court record compilation,
  correlation matrix generation, Syncfusion grid deployment, automated
  test validation, and 3-location backup. Use when new evidence arrives or
  when running a full forensic audit cycle.
---

# OSINT Forensic Evidence Pipeline

## Overview

End-to-end workflow that takes raw evidence (photos, documents, court records)
and produces court-ready indexed, cross-referenced, and verified forensic
intelligence products. Every run follows the Makaveli Protocol: zero noise,
absolute accountability, 3-location backup before and after.

## Dependencies

- **credentials** skill: For API key verification (Google Photos, Drive, BigQuery)
- **osint** skill: For supplementary OSINT tool integration
- **bigquery-sql** skill: For graph queries against `noble-beanbag-497411-m4`

## Quick Start

When the user says "run the pipeline", "process new evidence", "full audit cycle",
or "ingest batch N", follow the workflow below in order.

## Workflow

### Phase 0: Pre-Flight — Backup First (MANDATORY)

> [!CAUTION]
> Per AGENTS.md Rule 1: **No file is touched until backups at all 3 locations
> are confirmed current.** Run this BEFORE any changes.

1. Run the 3-location backup script:
   ```bash
   python scripts/backup_repo_3way.py
   ```
2. Verify all 3 locations report success:
   - GitHub: `git push origin main` (run from `C:\OsintNeoAi`, NOT OneDrive)
   - Local: `C:\Users\HP\OneDrive\Documents\OsintNeoAi\backups\repo\`
   - Google Drive: `gdrive:Sharedall/OsintNeoAi/` via rclone

If any backup fails, fix it before proceeding.

---

### Phase 1: Evidence Ingestion

Ingest raw evidence from source platforms into `evidence/` directory.

#### Step 1A: Google Photos Evidence
- Pull photo batches using `scripts/ocr_photos_batch.py`
- Photos land in `evidence/google_photos_evidence/` (and batch2, batch3, etc.)
- Each batch should be numbered sequentially (batch1, batch2, ... batch8+)

#### Step 1B: Google Drive / OneDrive Documents
- Use `download_gdrive_assets.py` for Google Drive files
- Use `onedrive_ingestion_engine.py` for OneDrive documents
- PDF evidence files go to `evidence/` root
- Lawsuit documents go to `evidence/lawsuit_info_full_dimarcello/`

#### Step 1C: Court Records
- Official court documents go to `evidence/official_court_records/`
- Run `scripts/compile_official_court_records.py` to generate the master index
- Output: `evidence/official_court_records/OFFICIAL_DOCUMENTS_INDEX.md`

> [!IMPORTANT]
> Per AGENTS.md Rule 2: NEVER delete existing evidence files. New versions
> are created alongside old ones. The owner consolidates.

---

### Phase 2: Bulk OCR Processing

Run neural OCR across all unprocessed photo evidence.

#### For a specific batch (preferred):
```bash
python scripts/ocr_batch8_full.py
```

#### For fast multi-threaded processing of all photos:
```bash
python scripts/fast_multithread_ocr_all_photos.py
```

#### For deep neural OCR on critical evidence:
```bash
python scripts/deep_neural_ocr_evidence.py
```

#### For DiMarcello lawsuit-specific evidence:
```bash
python scripts/ocr_dimarcello_evidence.py
```

**Output:** OCR transcripts land in:
- `evidence/ocr_transcripts_photos/` (general)
- `evidence/lawsuit_info_full_dimarcello/ocr_transcripts/` (lawsuit-specific)

**Validation:** Each transcript file should be non-empty. Check:
```bash
Get-ChildItem evidence/ocr_transcripts_photos/*.txt | Where-Object { $_.Length -eq 0 }
```
Any empty files indicate OCR failures that need re-processing.

---

### Phase 3: Entity Extraction & Graph Cross-Referencing

Cross-reference extracted entities against the BigQuery knowledge graph.

1. Run entity extraction from OCR transcripts:
   ```bash
   python extract_graph.py
   ```
   - Input: OCR transcripts + existing `nodes.json` / `edges.json`
   - Output: Updated `nodes.json`, `edges.json`

2. Cross-reference against BigQuery datasets:
   - `ppp_rico` — PPP loan fraud correlations
   - `forensic_layers.fca_timeline` — FCA whistleblower timeline
   - `national_audits.all_state_records` — Corporate/municipal records
   - `drive_forensics.drive_documents` — Drive content

3. Run the correlation engine:
   ```bash
   python aegis_correlation_engine.py
   ```
   - Output: `alerts_flagged.json`, `aegis_output.log`

4. Generate the master correlation matrix:
   ```bash
   python scripts/generate_master_correlation_matrix.py
   ```

**Key metrics to report:**
- Total nodes / edges in graph
- New entities discovered this cycle
- Flagged anomalies count

---

### Phase 4: Legal Briefing & Court Record Compilation

Generate court-ready intelligence products.

1. **Compile official court record index:**
   ```bash
   python scripts/compile_official_court_records.py
   ```

2. **Generate RICO analysis (if applicable):**
   ```bash
   python scripts/generate_rico_retaliation_audit.py
   ```

3. **Generate statutory audit report:**
   ```bash
   python scripts/edu_legal_statutory_audit.py
   ```

4. **Update briefings directory** — Create or update markdown briefings in
   `briefings/` for any new findings. Follow naming convention:
   `TOPIC_NAME_AUDIT_2026.md`

5. **Update the Syncfusion enterprise grid** with new verified facts:
   - Add FACT entries to `public/syncfusion_grid_v3_steroids.html`
   - Each fact must have: ID, claim, source, verification status, statutory ref

---

### Phase 5: Automated Validation

Run the full test suite to verify document integrity.

```bash
python -m pytest tests/ -v --tb=short
```

**Test tiers:**
1. `tests/test_official_documents.py` — Verifies all court records exist and contain required fields
2. `tests/test_adversarial_stress.py` — Stress tests against data integrity
3. `tests/test_adversarial_chains_challenger_2.py` — Adversarial chain validation

All tests MUST pass before proceeding to backup.

---

### Phase 6: Commit & 3-Location Backup (MANDATORY)

1. **Stage all new files:**
   ```bash
   git add -A
   ```

2. **Commit with descriptive message:**
   ```bash
   git commit -m "feat(evidence): [describe what was ingested/processed]"
   ```

3. **Run full 3-location backup:**
   ```bash
   python scripts/backup_repo_3way.py
   ```

4. **Verify the push succeeded:**
   ```bash
   git log --oneline -1
   ```

---

### Phase 7: Status Update

After every pipeline run, update:

1. **TASKS.md** — Mark any completed tasks, add new ones if discovered
2. **Daily report** — Update `reports/daily/DAILY_OSINT_REPORT_YYYY-MM-DD.md`
3. **Report to Architect** — Summarize:
   - Evidence ingested (count, type)
   - OCR transcripts generated
   - New graph entities/edges
   - Anomalies flagged
   - Tests passed/failed
   - Backup status (3/3 confirmed)

---

## Key File Locations

| Asset | Path |
|-------|------|
| Raw photo evidence | `evidence/google_photos_evidence*` |
| OCR transcripts | `evidence/ocr_transcripts_photos/` |
| Court records | `evidence/official_court_records/` |
| Lawsuit evidence | `evidence/lawsuit_info_full_dimarcello/` |
| Graph nodes | `nodes.json` |
| Graph edges | `edges.json` |
| Correlation alerts | `alerts_flagged.json` |
| Briefings | `briefings/` |
| Syncfusion grid | `public/syncfusion_grid_v3_steroids.html` |
| Test suite | `tests/` |
| Backup script | `scripts/backup_repo_3way.py` |
| Task ledger | `TASKS.md` |
| BigQuery project | `noble-beanbag-497411-m4` |

## Rate Limiting

- **Google Photos API:** 10,000 requests/day (free tier)
- **BigQuery:** 1TB free queries/month (sandbox mode)
- **rclone to Google Drive:** 10 files/second default

## Common Mistakes

1. **Running git from OneDrive path** — Always run git commands from
   `C:\OsintNeoAi`, never from the OneDrive sync path. OneDrive corrupts `.git`.

2. **Skipping backup before changes** — AGENTS.md Rule 1 is absolute.
   No exceptions. Backup first or fix the backup, then proceed.

3. **Deleting old evidence files** — NEVER. Create new versions alongside.
   `file_v2.py` lives next to `file.py`. Owner consolidates later.

4. **Overwriting another agent's work** — Multiple agents work this repo.
   If files already exist from another agent, create a separate version
   and document what changed.
