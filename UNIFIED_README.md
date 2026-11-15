# OsintNeoAi - Unified Index

Written 2026-11-14 at the owner's order: everything unified, in his own repo, reachable without depending on any one AI.

## What this repo is
The public index and public-safe snapshot of the OsintNeoAi library. It is NOT yet a complete copy of the library - see the counts below. It is the front door: what exists, where it lives, and what still has to move.

## Where everything lives (2026-11-14, measured)
- This repo: https://github.com/Tonypost949/OsintNeoAi - public site + NWO RICO Round-Up on `main` (~67 files); 15,745 unique paths across all 20 branches + 2 tags (measured 2026-11-06).
- The working library (Neo's VM workspace, ~/workspace): 440,649 files, 49.50 GB in this pass (excluding .git internals and the unification output folder itself; headline count earlier the same day was 441,426 files / 46 GB including those).
- Local repo checkouts inside that workspace: ~/workspace/osintneoai-github (old big checkout) and ~/workspace/github-consolidation/ (20 spare-profile repos, cloned 2026-10-31 so nothing is lost).
- The owner's PC (djdrop): C:\Amd949609_Antigravity_v1 - evidence locker, bridge, and staging.
- Backup drive (Samsung T7, D: on djdrop): audited 2026-11-06, report in the working library at ~/workspace/backup-drive-audit-2026-11-06/REPORT.md.
- Google Drive / Gmail / Photos: the owner's accounts, inventoried per-workstream in the library.
- Tasks: Google Tasks is the unified task list (owner's order 2026-11-14). The staged import and this package were prepared 2026-11-14 in ~/workspace/repo-unification-2026-11-14/.

## The gap, in numbers (this pass)
- In a local repo checkout (inside the workspace): 12,349 files
- Basename matches a repo-universe path, but the file itself sits outside any checkout (same name does NOT prove same content): 29,697 files
- Not in any repo by that method: 398,603 files - full list: not_in_any_repo_files.csv in the unification folder (not in this public export; it is an internal path list).
Full breakdown by folder: NOT_IN_ANY_REPO_SUMMARY.md in this export.

## What is deliberately NOT in this public repo
Credentials/keys, medical records, close family's full names (relationship labels only in public material), Takeout/mail archives, and binaries/large files. Counts per category are in NOT_IN_ANY_REPO_SUMMARY.md. Those need a private route, not a public push.

## Migration limit on the record
The GitHub connector snapshot route caps at 2,000 UTF-8 text files / 16 MB per push, no binaries. A full migration needs git pushes from a real checkout (or LFS / Drive) for the rest - staged, folder by folder, public-safe first.
