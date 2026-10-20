# TOOLS_LOG — OsintNeoAi tool inventory

Log of OSINT/AI tools for this project: what is installed, where, and its status.
Entries are only marked **installed** after the tool has actually been run and verified.

## Installed & verified

| Tool | Location | Runtime | Status | Verified |
|---|---|---|---|---|
| scanner/redact.py — fail-closed redaction & citation auditor | OsintNeoAi repo, `scanner/` | Python 3.12.3 (stdlib only) | Installed (local copy: ~/workspace/osintneoai/scanner/) | 2026-10-19 — ran in full pipeline |
| scanner/verify_public.py — post-scan verifier (secrets, SSNs, private IPs) | OsintNeoAi repo, `scanner/` | Python 3.12.3 (stdlib only) | Installed | 2026-10-19 — PASS on test input |
| scanner/sanitize_manifest.py — publish-safe manifest generator | OsintNeoAi repo, `scanner/` | Python 3.12.3 (stdlib only) | Installed | 2026-10-19 — ran in full pipeline |
| scanner/citation_report.py — citation coverage reporter | OsintNeoAi repo, `scanner/` | Python 3.12.3 (stdlib only) | Installed | 2026-10-19 — ran in full pipeline |
| scanner/run_scan.sh — pipeline runner | OsintNeoAi repo, `scanner/` | bash + python3 | Installed | 2026-10-19 — end-to-end run, exit 0 |

Dependencies: none beyond Python 3 standard library. No requirements.txt needed.

## Logged — not installed

| Tool | Source | Notes |
|---|---|---|
| Agent-Reach (Panniantong/Agent-Reach) | https://github.com/Panniantong/Agent-Reach — surfaced via Facebook Reel, 2026-10-19 | Claims to give an agent read access to Twitter/Reddit/YouTube/GitHub with zero paid APIs. NOT installed — third-party code, unverified; install only on explicit owner approval. |
| OX Alpha / "OpenFinisher" | Facebook Reel claim, 2026-10-19 | Unverified hype claim; no installable artifact identified. Logged for awareness only. |
| OSINTNeoAiCLI (Tonypost949/OSINTNeoAiCLI) | User's own repo (Python) | Sibling project; not yet installed or audited here. |

## Verification runs

- 2026-10-19: run_scan.sh against a Facebook post export (Anthony Greb, Nancy Guthrie case). Result: published, no redactions, verify PASS, citation gap = missing legal_section. Outputs in local output/ (PUBLIC_MANIFEST.json, VERIFY_REPORT.json, CITATION_GAPS.csv).
