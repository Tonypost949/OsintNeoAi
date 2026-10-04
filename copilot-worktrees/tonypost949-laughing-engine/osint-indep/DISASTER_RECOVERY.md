# Disaster Recovery & Resurrection Procedure

**Version:** 1.0  
**Last Tested:** [DATE - UPDATE AFTER EACH TEST]  
**Tested By:** [AGENT NAME]  
**Restore Time:** [TARGET < 30 MINUTES]

---

## Overview

This document describes the complete procedure to resurrect the OSINT Independent Platform from **zero infrastructure** to **fully operational** using only the backup tiers.

**Recovery Time Objective (RTO):** 30 minutes  
**Recovery Point Objective (RPO):** 2 hours (max backup age)

---

## Tier Priority for Recovery

1. **Tier 2 (Google Drive `sharedall`)** - Primary: Complete repo + large assets + AI tool clones
2. **Tier 3 (Local `C:\osint-indep-backup`)** - Secondary: Identical to Tier 2, faster access
3. **Tier 1 (GitHub)** - Tertiary: Code only, no large assets
4. **Tier 4 (Cold Storage)** - Last resort: Monthly bundles

---

## Prerequisites (Target Machine)

- Windows 10/11 or Linux (Ubuntu 22.04+)
- 16GB+ RAM, 100GB+ free disk
- Internet access (for Google Drive download)
- Admin/sudo privileges

---

## Recovery Procedure

### Phase 1: Bootstrap (5 minutes)

#### Option A: From Google Drive (Preferred)

```bash
# 1. Install rclone
# Windows:
#   Download from https://rclone.org/downloads/
#   Add to PATH
# Linux:
curl https://rclone.org/install.sh | sudo bash

# 2. Configure rclone for sharedall drive
# You need the service account JSON from the repo maintainer
rclone config create gdrive-sharedall drive \
  scope=drive \
  service_account_file=/path/to/service-account.json \
  team_drive=[SHARED_DRIVE_ID]

# 3. Verify access
rclone lsd gdrive-sharedall:osint-indep-backup/
```

#### Option B: From Local Backup (Fastest)

```bash
# If local backup drive is connected
cp -r /mnt/e/osint-indep-backup/latest /target/restore/path
# OR Windows:
xcopy E:\osint-indep-backup\latest C:\restore\path /E /I /H
```

### Phase 2: Restore Repository (10 minutes)

```bash
# 1. Extract latest snapshot
cd /target/restore/path

# If you have the git bundle (fastest):
git clone osint-indep-backup/snapshots/latest.bundle osint-indep
cd osint-indep

# OR if you have the full folder:
# Already there, just verify .git exists
ls -la .git/
```

### Phase 3: Restore Large Assets (10 minutes)

```bash
# 1. Download vendor assets (frontend deps)
rclone sync gdrive-sharedall:osint-indep-backup/latest/vendor ./vendor --progress

# 2. Download model weights
rclone sync gdrive-sharedall:osint-indep-backup/latest/models ./models --progress

# 3. Download build tools (AI clones, runtimes)
rclone sync gdrive-sharedall:osint-indep-backup/latest/build-tools ./build-tools --progress

# 3. Verify all assets
./scripts/verify-assets.sh
```

### Phase 4: Environment Setup (5 minutes)

```bash
cd osint-indep

# 1. Run environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install Python deps (from vendored wheels if offline)
pip install --no-index --find-links=./vendor/wheels -r requirements.txt

# 3. Initialize database
python -m src.core.database init

# 4. Load config
cp config/default.yaml config/local.yaml
# Edit config/local.yaml with your API keys
```

### Phase 5: Verification (5 minutes)

```bash
# 1. Run health checks
python -m scripts.health_check

# 2. Run test suite
pytest tests/ -x -q

# 3. Start API server
python -m src.api.routes

# 4. Verify web UI
curl -f http://localhost:8080/health

# 5. Test collectors
python -c "
from src.collectors import CollectorRegistry
reg = CollectorRegistry()
print('Registered:', reg.list_collectors())
"
```

---

## Verification Checklist

| Component | Test Command | Expected |
|-----------|--------------|----------|
| Git repo | `git log --oneline -1` | Shows latest commit |
| Python env | `python -c "import src"` | No import errors |
| Database | `python -m src.core.database check` | "OK" |
| API server | `curl localhost:8080/health` | `{"status":"ok"}` |
| Collectors | `python -m src.collectors.test_all` | All pass |
| Web UI | Open `localhost:8080` | Loads without errors |
| Assets | `./scripts/verify-assets.sh` | All checksums match |
| Models | `python -c "from src.enrichers import *; print('OK')"` | No errors |

---

## Post-Recovery Actions

1. **Update backup timestamps** - Run `./scripts/sync-all.sh` immediately
2. **Rotate API keys** - If compromise suspected, regenerate all keys
3. **Document incident** - Add entry to `INCIDENT_LOG.md`
4. **Schedule full test** - Next monthly resurrection drill

---

## Resurrection Test Log

| Date | Tester | Source Tier | Restore Time | Issues | Status |
|------|--------|-------------|--------------|--------|--------|
| 2026-01-15 | [NAME] | Tier 2 (GDrive) | 22 min | Model download slow | ✅ PASS |
|  |  |  |  |  |  |

---

## Emergency Contacts

| Role | Name | Contact | Backup Access |
|------|------|---------|---------------|
| Primary Maintainer | [NAME] | [CONTACT] | Full |
| Secondary | [NAME] | [CONTACT] | Tier 2/3 |
| Infrastructure | [NAME] | [CONTACT] | Tier 1/2/3 |

---

## Appendix: Service Account Setup (For New Recovery Machines)

```bash
# 1. Get service account JSON from maintainer (encrypted)
# 2. Save as /etc/osint-indep/gdrive-sa.json (Linux) or C:\osint-indep\gdrive-sa.json (Windows)
# 3. Set permissions
chmod 600 /etc/osint-indep/gdrive-sa.json

# 4. Configure rclone
rclone config create gdrive-sharedall drive \
  scope=drive \
  service_account_file=/etc/osint-indep/gdrive-sa.json \
  team_drive=[SHARED_DRIVE_ID_FROM_MAINTAINER]

# 5. Test
rclone lsd gdrive-sharedall:osint-indep-backup/
```

---

## Appendix: Manual GitHub-Only Recovery (If All Else Fails)

```bash
# 1. Clone from GitHub (code only)
git clone https://github.com/Tonypost949/OsintNeoAi.git osint-indep
cd osint-indep
git checkout sentinel-edition

# 2. Manually download vendor assets from releases or maintainer
# 3. Manually download models from maintainer
# 4. Recreate build-tools from BUILD_ENVIRONMENT.md
# 5. This path takes 2-4 hours - avoid if possible
```

---

**Remember: The best disaster recovery is the one you've tested. Run monthly drills.**