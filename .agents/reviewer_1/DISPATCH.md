# Dispatch Instructions for reviewer_1

## Identity & Role
- Role: Code Reviewer & Quality Auditor (R1 Backlog Tasks)
- Archetype: teamwork_preview_reviewer
- Working directory: C:\OsintNeoAi\.agents\reviewer_1
- Parent: orchestrator_13 (e68e15f5-4a37-405f-8e73-c5b57613b6cf)

## Scope
Review the R1 deliverables:
1. `data/tasks.json`, `cli/data/tasks.json`, and `TASKS.md` for TASK-069, TASK-070, TASK-072, TASK-074, TASK-076, and TASK-078.
2. Confirm that each task transitioned to DONE has a valid, genuine implementation file and corresponding artifact.
3. Run `python tests/run_milestone_tests.py` and `python -m unittest tests/test_official_documents.py`.
4. Render an explicit verdict: APPROVE or REQUEST_CHANGES.

Read:
- C:\OsintNeoAi\.agents\ORIGINAL_REQUEST.md
- C:\OsintNeoAi\AGENTS.md
- C:\OsintNeoAi\.agents\worker_impl_m1_m2\handoff.md

Write `report.md` and `handoff.md` with your verdict and findings, and message parent.

## 2026-09-10T19:09:08Z
You are reviewer_1.
Your working directory is C:\OsintNeoAi\.agents\reviewer_1.
Read C:\OsintNeoAi\.agents\ORIGINAL_REQUEST.md, C:\OsintNeoAi\AGENTS.md, and C:\OsintNeoAi\.agents\reviewer_1\DISPATCH.md.
Also read C:\OsintNeoAi\.agents\worker_impl_m1_m2\handoff.md.

Review R1 task backlog updates in data/tasks.json, TASKS.md, and cli/data/tasks.json.
Run tests: python tests/run_milestone_tests.py and python -m unittest tests/test_official_documents.py.
Write report.md and handoff.md with an explicit verdict (APPROVE or REQUEST_CHANGES).
Message parent with your findings.
