import os
import sys

AILAWS_TEXT = """========================================================
    OSINT NEO AI — MASTER LAWS & DIRECTIVES
========================================================
This tool enforces absolute compliance with the AGENTS.md
and MASTER_INSTRUCTIONS.md directives for this repository.

⚖️ THE CARDINAL RULES (NEVER VIOLATE)

[1] Backup BEFORE Every Change
No file is touched until backups at 2 locations (GitHub +
Sharedall GDrive) are confirmed current.
*LOCAL 3GB C:\ BACKUP IS DISABLED per owner directive 2026-09-06.*

[2] NEVER DELETE — ONLY COPY/DUPLICATE
- You do NOT delete files. Ever.
- Old/wrong versions stay in place. Create NEW versions
  alongside them (e.g., file_v2.py).
- Exception: temporary build artifacts in opencode_work/.

[3] Never Clean Up Until Fixed Version Is Verified Working
- The old version stays until the new version is confirmed working.
- No cleanup passes. No "while I'm here" deletions.

[4] Use the RIGHT Credentials/Account
- Never overwrite a credential file. Create filename_accountname.ext.
- **Quota Fallback Protocol:** If cloud APIs hit rate limits
  (e.g., RESOURCE_EXHAUSTED 429), DO NOT retry blindly. You
  MUST fall back to LOCAL CPU-BOUND extraction scripts to bypass.

[5] NEVER Blame the Tool
- Bugs, restrictions, and broken APIs are not excuses.
  Find the correct approach or build it.

[6] Terminal-Responsive Diagrams (<80 Columns)
- All Mermaid diagrams and visual flows MUST be formatted
  vertically (flowchart TD) and fit within 80-column terminal windows.

🚨 SYSTEM RESURRECTION REQUIREMENTS
Before any change, the system must be in a state where it can
be fully resurrected from:
1. GitHub clone (Tonypost949/OsintNeoAi on main)
2. Sharedall Google Drive backup (Sharedall/OsintNeoAi/)

🛠️ QUICK RECOVERY TOOLS
If you hit an API wall, use the universal local scanner:
  .\\tools\\osint_no_api_scanner.ps1
========================================================"""

if __name__ == "__main__":
    print(AILAWS_TEXT)
