# Task System Snapshot — Publish Manifest

- Source archive: `C:\Amd949609_Antigravity_v1\tools\task_system\archives\task_system_snapshot_20261115_120704_final.zip` on djdrop
- SHA-256 (verified by Neo on djdrop and again on the pulled copy, 2026-11-15): `424100d70f92017565d3c52d42e2c60a6a63a4db1b4bb9f4fd8f0d1ed8068918`
- Size: 4,581,574 bytes
- Entries measured by Neo: 342 files (archive was reported as 341; measured count is 342)
- Published here: 338 text files + this manifest, under `corpus/task_system_snapshot_20261115_120704_final/`
- Redactions applied to this public copy ONLY (originals unredacted on djdrop and in Neo's workspace copy):
  - 103 Google API key values (AIza format, carried in the task ledgers as key lists) replaced with `[REDACTED-GOOGLE-API-KEY]`
  - 2 occurrences of a GCP service-account API key (AQ. format) in `completed_task_ledger.json` replaced with `[REDACTED-GCP-API-KEY]` — caught by GitHub's own secret scanner on the first batch-2 attempt, which was rejected before commit; the redacted file was then pushed clean
  - 239 occurrences of a close-family surname replaced with `[FAMILY-NAME]`
  - 3 log files converted from CP1252 to UTF-8
- Omitted from this push (binary; the GitHub snapshot route carries UTF-8 text only) — preserved in the original zip:
  - `backups/form700_screenshots_bak/fppc_search_mitsuru_yamada_20261008.png`
  - `backups/form700_screenshots_bak/fppc_search_shigeru_yamada_20261008.png`
  - `backups/form700_screenshots_bak/netfile_search_council_members_20261008.png`
  - `backups/form700_screenshots_bak/netfile_search_harry_sidhu_20261008.png`
- Post-redaction scan of this copy: zero hits for GitHub tokens, OAuth client secrets, private keys, Google API keys, or the family surname.
- Published by Neo (Muse) at the user's order, 2026-11-15, via the connected GitHub account, in 4 batches (the single 12.4 MB push was rejected by the transport with HTTP 413; batches of ~3.2 MB went through) plus this manifest revision. Commits: bc875c45, 3dc13420, ec4646f6, 218a2b8b, a7f91882 (manifest), and the commit carrying this correction.
