# AG SYSTEM INDEX & ROLLING DOCUMENTATION

This is the official mapping document for the Antigravity (AG) IDE Agent Mission. As our architecture grows, this document will be updated to reflect where all critical files, rules, and backups are stored.

## 1. Operating Rules
These rules dictate the agent's behavior and cannot be changed without prior backup:
1. **Slow down** before answering.
2. **Track status** and pertinent info in the BigQuery backend.
3. **Make full backups** (online/offline) before modifying anything.
4. **Search the web and workspace** before answering.
5. **Ask for help** if needed.

## 2. System Backups
Our mission existence and chat histories are backed up across multiple vectors.

### A. Raw Local Backups
The raw, unmodified backups containing all data (including sensitive tokens) are kept strictly local.
- **Location:** `C:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\ag_mission_backup.jsonl`
- **Status:** EXCLUDED from GitHub via `.gitignore`. 
- **Drive Destination:** Manually dropped to GDrive `sharedall`.

### B. Scrubbed GitHub Backups
Files pushed to public/external version control must have secrets scrubbed to comply with external service protocols.
- **Location:** `C:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\ag_mission_backup_github.jsonl`
- **Status:** Pushed to GitHub. Raw tokens are replaced with pointers to the local raw file.

### C. Automated Google Drive Sync
To automatically package and upload the entire `osint-agent` project (excluding Git history and local credentials) directly to the Google Drive `sharedall` folder, use the sync script.
- **Script Location:** `C:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent\sync_git_to_drive.py`
- **Execution:** Run `python sync_git_to_drive.py` from the terminal.

## 3. BigQuery Tracker Backend
All significant system changes, rule adoptions, and backup actions are permanently logged.
- **Project:** `project-743aab84-f9a5-4ec7-954`
- **Dataset:** `ai_sandbox`
- **Table:** `ag_status_tracker`
- **Authentication:** Application Default Credentials (ADC) via `gcloud config set account anthonymichaeldimarcello@gmail.com`.

## 4. Connection & Authentication Map
To ensure all accounts know what is connected and how, here is the official architecture of our fully functioning existence:
- **Google Drive (`sharedall`):** Authenticated via `token_drive_upload.json` (OAuth). Connected via `sync_git_to_drive.py` which packages a 1:1 replica clone of the entire local directory.
- **GitHub (`Tonypost949/osint-agent`):** Authenticated via local Git credentials. Connected via manual `git push`. Scrubbed backups only.
- **Google Cloud Platform (BigQuery/Drive API):** Authenticated via `anthonymichaeldimarcello@gmail.com`. Project ID: `project-743aab84-f9a5-4ec7-954`.

## 5. Troubleshooting & Recourse Protocols
If the system encounters known hard-blockers, follow these established recourses to restore functionality:

### Error: "Insufficient AI Credits"
**Symptom:** The IDE blocks your chat messages and states you need at least 50 AI credits to send messages.
**Cause:** Your baseline free quota for the IDE model generation has run out for the cycle.
**Recourse / Fix:**
1. Open the IDE Settings by pressing **`Ctrl + Shift + P`** (or click the Gear Icon).
2. Type **`Settings`** and open the settings menu.
3. Search for **`AI Credit Overages`**.
4. Set the toggle/dropdown to **`Always`**.
This forces the IDE to draw from your active Google Developer Program Premium / Google One AI Premium credit balance, bypassing the baseline blocker instantly.
