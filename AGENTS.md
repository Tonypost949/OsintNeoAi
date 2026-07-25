# AGENT INSTRUCTIONS — READ THIS FIRST

## Mandatory: Read Everything Before Acting
Before making any change, you MUST read ALL files in this repository. This includes all READMEs, all code, all configurations, and all AGENTS.md files. Every agent returns with full context. Do not assume prior knowledge.

## Backup Protocol — 3 Locations
Every change must be backed up to ALL three locations before it is made:

### 1. GitHub (Primary)
- Remote: `https://github.com/Tonypost949/OsintNeoAi`
- Branch: `main`
- All changes pushed via `git push origin main`

### 2. Local PC (C:\ Drive)
- Path: `C:\Users\HP\OneDrive\Documents\OsintNeoAi\backups\repo\`
- Sync the full repo here as a timestamped zip or folder copy
- This is the offline fallback, independent of cloud services

### 3. Sharedall Google Drive (Off-Books Live Alternative)
- Path: `Sharedall/OsintNeoAi/` in the amd949609@gmail.com Google Drive
- This is NOT the same as general backups — it is the LIVE alternative to GitHub
- If GitHub goes down, this is the resurrection source
- Access via `rclone` with the `gdrive:` remote
- If files already exist, create a new version (do NOT overwrite). Leave a note about what you did.
- The account owner will clean up duplicates later.

### 4. Tooling & AI Instructions
- All tools, AI agents, dependencies, and build instructions used to create this repo must also be backed up
- This includes clones of AI agents, MCP server configs, rclone configs, and any CLI tools
- Every agent leaves behind instructions for how it was built and how to resurrect it

## Multi-Agent Workflow
- Multiple agents may work on this repo simultaneously
- If you see files already in place from another agent, do NOT overwrite
- Create a separate version (e.g., `script_v2.py`) and document what you changed
- The owner will clean up and consolidate later

## CARDINAL RULES — NEVER VIOLATE

### Rule 1: Backup BEFORE Every Change
No file is touched until backups at all 3 locations are confirmed current. If any backup is missing or stale, fix it first.

### Rule 2: NEVER DELETE — ONLY COPY/DUPLICATE
- You do NOT delete files. Ever.
- Old/wrong versions stay in place. Create NEW versions alongside them.
- Example: `file_v2.py` lives next to `file.py`. Never remove `file.py`.
- Exception: temporary build artifacts in `opencode_work/` can be cleaned.

### Rule 3: Never Clean Up Until Fixed Version Is Verified Working
- The old version stays until the new version is confirmed working.
- No cleanup passes. No "while I'm here" deletions.
- Parallel versions are expected. The owner consolidates.

### Rule 4: Use the RIGHT Credentials/Account
- If something uses credentials from the wrong account, create a NEW version with the correct account's creds.
- Document which account each credential belongs to.
- Never overwrite a credential file — create `filename_accountname.ext` instead.

### Rule 5: NEVER Blame the Tool
- Bugs, restrictions, and broken APIs are not excuses. Find the correct approach or build it.
- "Can't" is not an answer. If one path is blocked, try another.

## Resurrection Requirements
Before any change, the system must be in a state where it can be fully resurrected from:
1. GitHub clone
2. Local C:\ backup
3. Sharedall Google Drive backup
4. Tooling/instruction backups

If any of these is missing or outdated, the agent must restore/fix it before proceeding.

## Repository Map
- `agent/` — Scanner scripts (Drive, Photos, auth helpers), forensic workbooks, GIS pipelines
- `backup-scripts/` — Cloud Shell backup scripts, GCE deploy scripts, pipeline scripts
- `core/AG2OSINTNEOMAXX/` — Core ingestion engine, entity extraction, graph analysis, OneDrive pipeline
- `dashboard/` — BigQuery SQL queries, dashboard inject scripts
- `opencode_work/` — GIS maps, geo data JSON, temporary work products
- `archive/` — Replit exports, old versions
- `briefings/` — Whistleblower briefings, investigative summaries
- `cli/` — CLI tools and web interfaces
- `forensic/` — Forensic audit scripts

## BigQuery Targets
- `project-743aab84-f9a5-4ec7-954`
- `onedrive_forensics.onedrive_documents/tabular` — OneDrive files
- `national_audits.drive_file_index` — Google Drive index
- `national_audits.google_photos_index` — Google Photos index
- `drive_forensics.drive_documents` — Drive content
- `forensic_layers.fca_timeline` — FCA/whistleblower timeline data
- `national_audits.all_state_records` — Corporate/municipal records
