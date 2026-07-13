# BACKUP PROTOCOL - MANDATORY READING FOR ALL AGENTS

## YOU ARE AN AGENT WORKING ON THIS REPO

**STOP. READ THIS ENTIRE FILE BEFORE DOING ANYTHING.**

If you are an AI agent, coding assistant, or automated tool that has been given access to this repository, you MUST read and follow this protocol before making ANY changes. This is not optional. This is not a suggestion. This is the law of this repo.

---

## TABLE OF CONTENTS

1. [What This Repo Is](#what-this-repo-is)
2. [Backup Architecture](#backup-architecture)
3. [Backup Locations](#backup-locations)
4. [Pre-Change Protocol](#pre-change-protocol)
5. [Post-Change Protocol](#post-change-protocol)
6. [Resurrection Instructions](#resurrection-instructions)
7. [Tools and Dependencies](#tools-and-dependencies)
8. [Agent Checklist](#agent-checklist)

---

## What This Repo Is

This is the **OsintNeoAi** repository - an OSINT (Open Source Intelligence) investigation platform. It contains:

- Multiple OSINT tools and editions (including `sentinel-edition/`)
- Investigation data and forensic analyses
- BigQuery pipelines and data connectors
- AI agent configurations
- Deployment scripts for Google Cloud Run

**CRITICAL**: This repo is the PRIMARY copy. But it is NOT the only copy. There are redundant backups that must ALWAYS be kept in sync.

---

## Backup Architecture

```
                    ┌─────────────────────────┐
                    │   GITHUB REPO (PRIMARY) │
                    │   Tonypost949/OsintNeoAi│
                    └──────────┬──────────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
    ┌─────────────────┐ ┌──────────────┐ ┌──────────────────┐
    │ LOCAL C: DRIVE  │ │ SHAREDALL    │ │ GIT CLONES       │
    │ (C:\Users\HP\   │ │ (Google Drive│ │ (Additional      │
    │  OneDrive\      │ │  Backup)     │ │  safety copies)  │
    │  Documents\     │ │              │ │                  │
    │  opencode_work) │ │              │ │                  │
    └─────────────────┘ └──────────────┘ └──────────────────┘
```

### The Three Pillars of Backup

1. **GitHub Repo** (Primary) - The main codebase at `https://github.com/Tonypost949/OsintNeoAi`
2. **Local C: Drive** - `C:\Users\HP\OneDrive\Documents\opencode_work\` (synced via OneDrive)
3. **SharedAll Drive** - Google Drive shared folder used as off-the-books backup in case GitHub goes down

---

## Backup Locations

### PRIMARY: GitHub Repository
- **URL**: `https://github.com/Tonypost949/OsintNeoAi`
- **Branch**: `main`
- **Purpose**: Primary development, collaboration, CI/CD
- **Auto-sync**: GitHub Actions push hourly via `auto-commit.yml`

### LOCAL: C: Drive (OneDrive-Synced)
- **Path**: `C:\Users\HP\OneDrive\Documents\opencode_work\`
- **Purpose**: Local development, offline access, working copies
- **Sync**: OneDrive auto-syncs to Microsoft cloud
- **Contains**: Full workspace including `sentinel-edition/`, scripts, data

### OFF-THE-BOOKS: SharedAll (Google Drive)
- **Purpose**: Redundant backup if GitHub or OneDrive goes down
- **Access**: Google Drive API or rclone
- **Folder**: Shared with specific collaborators
- **Format**: ZIP archives of entire repo states + individual file backups
- **Backup scripts**: `full_backup_to_sharedall.py`, `backup_opencode_work_to_sharedall.py`

### LOCAL BACKUP FOLDERS
- `C:\Users\HP\OneDrive\Documents\github_backups\` - GitHub repo snapshots
- `C:\Users\HP\OneDrive\Documents\opencode_work_backup\` - Workspace backups
- `C:\Users\HP\OneDrive\Documents\OsintNeoAi_backup\` - Dedicated repo backup

---

## Pre-Change Protocol

**BEFORE YOU MAKE ANY CHANGE TO THIS REPO, YOU MUST:**

### Step 1: Read Everything
- Read this `BACKUP_PROTOCOL.md` completely
- Read the `README.md` of whatever edition you are working on
- Read any `CHANGELOG.md` or `session_summary_*.md` files
- Check recent git commits: `git log --oneline -20`
- Check for open PRs: `gh pr list`

### Step 2: Create a Backup
```bash
# Create a timestamped backup before ANY changes
python sentinel-edition/backup/create_backup.py

# Or manually:
# 1. Zip the current state
# 2. Copy to C:\Users\HP\OneDrive\Documents\github_backups\
# 3. Upload to SharedAll via backup script
# 4. Commit current state to git
```

### Step 3: Verify Backups Exist
```bash
# Run verification
python sentinel-edition/backup/verify_backups.py
```

### Step 4: Document What You Are About to Do
- Add a note to `CHANGELOG.md` or relevant `session_summary_*.md`
- Describe what changes you plan to make
- Note which files you will modify

---

## Post-Change Protocol

**AFTER YOU MAKE ANY CHANGE TO THIS REPO, YOU MUST:**

### Step 1: Test Your Changes
```bash
# Run tests if applicable
python sentinel-edition/tests/test_engine.py

# Verify nothing is broken
python sentinel-edition/backup/verify_backups.py
```

### Step 2: Commit to Git
```bash
git add -A
git commit -m "Description of what changed"
git push origin main
```

### Step 3: Trigger Backup Sync
```bash
# Backup to SharedAll
python sentinel-edition/backup/sync_to_sharedall.py

# Backup to local folders
python sentinel-edition/backup/sync_to_local.py
```

### Step 4: Update Session Summary
- Create or update `session_summary_YYYYMMDD.md`
- Document what was done, what changed, what is next

---

## Resurrection Instructions

If this repo is ever lost, deleted, or compromised, here is how to resurrect it:

### From GitHub (Primary)
```bash
git clone https://github.com/Tonypost949/OsintNeoAi.git
cd OsintNeoAi
pip install -r requirements.txt  # or sentinel-edition/requirements.txt
python sentinel-edition/tests/test_engine.py  # verify
```

### From Local C: Drive
```bash
# Navigate to local copy
cd C:\Users\HP\OneDrive\Documents\opencode_work\OsintNeoAi
# or
cd C:\Users\HP\OneDrive\Documents\opencode_work
# The sentinel-edition is directly here
```

### From SharedAll (Google Drive)
```bash
# Use the download script
python sentinel-edition/backup/download_from_sharedall.py

# Or manually:
# 1. Go to Google Drive
# 2. Find the shared "OsintNeoAi" backup folder
# 3. Download the latest ZIP
# 4. Extract to your working directory
```

### From Local Backup Folders
```bash
# Check these locations for recent backups:
dir C:\Users\HP\OneDrive\Documents\github_backups\
dir C:\Users\HP\OneDrive\Documents\opencode_work_backup\
dir C:\Users\HP\OneDrive\Documents\OsintNeoAi_backup\
```

### Full Resurrection Checklist
1. [ ] Clone from GitHub OR download from SharedAll OR copy from local backup
2. [ ] Install dependencies: `pip install -r requirements.txt`
3. [ ] Run tests: `python sentinel-edition/tests/test_engine.py`
4. [ ] Verify config: `cp sentinel-edition/config/config.example.json sentinel-edition/config/config.json`
5. [ ] Check backup sync is working: `python sentinel-edition/backup/verify_backups.py`
6. [ ] Update any hardcoded paths if needed
7. [ ] Re-enable GitHub Actions workflows if needed

---

## Tools and Dependencies

### Required for Backup Operations
- **Python 3.10+** - All backup scripts are Python
- **requests** - For Google Drive API calls
- **zipfile** (stdlib) - For creating ZIP archives
- **shutil** (stdlib) - For file copying
- **subprocess** (stdlib) - For git operations

### Optional Tools
- **rclone** - For Google Drive sync (installed at `C:\Users\HP\OneDrive\rclone-v1.74.1-windows-amd64\`)
- **gh** (GitHub CLI) - For PR management and releases
- **git** - For version control

### Backup Script Locations
All backup scripts live in `sentinel-edition/backup/`:
- `create_backup.py` - Creates timestamped ZIP archive
- `sync_to_sharedall.py` - Uploads to Google Drive SharedAll folder
- `sync_to_local.py` - Copies to local backup folders
- `download_from_sharedall.py` - Downloads from SharedAll
- `verify_backups.py` - Checks all backup locations are current
- `pre_change_backup.py` - Automated pre-change backup (run this first)

---

## Agent Checklist

Before ANY agent touches this repo, they must confirm:

- [ ] I have read `BACKUP_PROTOCOL.md` (this file)
- [ ] I have read the relevant `README.md`
- [ ] I have checked recent git history (`git log --oneline -20`)
- [ ] I have created a backup before making changes
- [ ] I understand where backups are stored
- [ ] I know how to verify backups are current
- [ ] I will create a session summary after my work
- [ ] I will run post-change backup sync

**If you cannot confirm all of the above, DO NOT MAKE CHANGES.**

---

## Notes for Other Agents

- If you see existing backup scripts, check their timestamps before creating new ones
- Multiple agents may work on this repo simultaneously - always check `git status` before committing
- If a backup script already exists that does what you need, use it - don't create duplicates
- The SharedAll backup is the OFF-THE-BOOKS backup - keep it updated
- Always leave notes about what you changed and why
- The `sentinel-edition/` is an INDEPENDENT edition - it does not depend on the rest of the repo

---

## Backup Schedule

| Backup Type | Frequency | Method |
|------------|-----------|--------|
| Git commit | After every change | `git push` |
| Local C: drive | Real-time | OneDrive auto-sync |
| SharedAll | After significant changes | `sync_to_sharedall.py` |
| GitHub Actions | Hourly | `auto-commit.yml` workflow |
| Full archive | Weekly | `create_backup.py` |

---

## Emergency Contacts

If backups are failing or you need help:
- Check GitHub Issues: `https://github.com/Tonypost949/OsintNeoAi/issues`
- Owner: `Tonypost949` (Anthony DiMarcello)
- Email: `anthony.dimarcello@students.post.edu`

---

**THIS FILE WAS LAST UPDATED: July 10, 2026**
**IF YOU ARE AN AGENT AND YOU HAVE NOT READ THIS ENTIRE FILE, STOP AND READ IT NOW.**
