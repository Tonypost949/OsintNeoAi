# Dispatch Instructions for auditor_1

## Identity & Role
- Role: Forensic Integrity Auditor
- Archetype: teamwork_preview_auditor
- Working directory: C:\OsintNeoAi\.agents\auditor_1
- Parent: orchestrator_13 (e68e15f5-4a37-405f-8e73-c5b57613b6cf)

## Scope
Perform forensic integrity verification across all work products of `worker_impl_m1_m2`:
1. Static Analysis & Authenticity Audit:
   - Check `api/workspace_intelligence.py` for genuine logic (no hardcoded return values, no mock dictionaries pretending to calculate distances, no fake datasets).
   - Check `api/main.py` modifications for genuine route handling and null-safety implementation.
   - Check `workspace_v2.html` and `templates/workspace_v2.html` for authentic UI code and 100% template parity.
   - Check `tests/test_workspace_intelligence.py` to ensure it exercises actual application code rather than trivial assertions.
2. Ledger & File System Audit:
   - Verify that NO files were deleted (AGENTS.md Rule 2).
   - Verify that `data/tasks.json` and `TASKS.md` task completions cite authentic script deliverables.
3. Runtime Integrity Audit:
   - Execute the test suites:
     - `python tests/run_milestone_tests.py`
     - `python -m unittest tests/test_workspace_intelligence.py`
     - `python -m unittest tests/test_genesis_ingest.py`
     - `python -m unittest tests/test_challenger1_genesis_hud_harness.py`
4. Render a binary verdict: CLEAN or INTEGRITY VIOLATION / CHEATING DETECTED.

Read:
- C:\OsintNeoAi\.agents\ORIGINAL_REQUEST.md
- C:\OsintNeoAi\AGENTS.md
- C:\OsintNeoAi\.agents\worker_impl_m1_m2\handoff.md

Write `report.md` and `handoff.md` with your verdict and findings, and message parent.

## 2026-09-10T19:10:00Z
You are auditor_1.
Your working directory is C:\OsintNeoAi\.agents\auditor_1.
Read C:\OsintNeoAi\.agents\ORIGINAL_REQUEST.md, C:\OsintNeoAi\AGENTS.md, and C:\OsintNeoAi\.agents\auditor_1\DISPATCH.md.
Also read C:\OsintNeoAi\.agents\worker_impl_m1_m2\handoff.md.

Conduct a forensic integrity audit of worker_impl_m1_m2's work products.
Verify authenticity (no mock stubs, no hardcoded cheating, no fake calculations), non-destructive compliance (zero file deletions per AGENTS.md Rule 2), and run test suites to verify genuine functionality.
Write report.md and handoff.md with an explicit verdict: CLEAN or INTEGRITY VIOLATION / CHEATING DETECTED.
Message parent with your findings.
