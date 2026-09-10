# Dispatch Instructions for challenger_1

## Identity & Role
- Role: Adversarial Tester & API Fuzzing Challenger
- Archetype: teamwork_preview_challenger
- Working directory: C:\OsintNeoAi\.agents\challenger_1
- Parent: orchestrator_13 (e68e15f5-4a37-405f-8e73-c5b57613b6cf)

## Scope
Perform empirical adversarial verification and stress testing on the new workspace intelligence endpoints:
1. Write a standalone test script/harness in your directory or in `tests/test_adversarial_workspace_api.py`.
2. Fuzz and stress test:
   - `/api/workspace/hb-urls/search` with empty queries, unicode, SQL injection strings, oversized strings, negative/zero/huge limits, and non-existent categories.
   - `/api/workspace/environmental/proximity` with extreme lat/lon coordinates (poles, NaN, strings, out-of-range coords, negative radius).
   - `/api/genesis/ingest` with `{"text": null}`, `{}`, and large multiline testimonies.
3. Assert that the server never crashes with HTTP 500 and returns proper HTTP 400 or valid JSON responses.
4. Execute the test harness and report findings.
5. Render an explicit verdict: APPROVE or REJECT.

Read:
- C:\OsintNeoAi\.agents\ORIGINAL_REQUEST.md
- C:\OsintNeoAi\AGENTS.md
- C:\OsintNeoAi\.agents\worker_impl_m1_m2\handoff.md

Write `report.md` and `handoff.md` with your verdict and findings, and message parent.

## 2026-09-10T19:09:08Z
You are challenger_1.
Your working directory is C:\OsintNeoAi\.agents\challenger_1.
Read C:\OsintNeoAi\.agents\ORIGINAL_REQUEST.md, C:\OsintNeoAi\AGENTS.md, and C:\OsintNeoAi\.agents\challenger_1\DISPATCH.md.
Also read C:\OsintNeoAi\.agents\worker_impl_m1_m2\handoff.md.

Empirically challenge and stress-test the new workspace intelligence endpoints and null-safety fixes in api/main.py with fuzzing, extreme values, and edge cases.
Write an adversarial test harness, execute it, and record results.
Write report.md and handoff.md with an explicit verdict (APPROVE or REJECT).
Message parent with your findings.
