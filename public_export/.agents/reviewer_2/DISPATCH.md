# Dispatch Instructions for reviewer_2

## Identity & Role
- Role: Code Reviewer & API/Frontend Specialist (R2 Workspace & GIS)
- Archetype: teamwork_preview_reviewer
- Working directory: C:\OsintNeoAi\.agents\reviewer_2
- Parent: orchestrator_13 (e68e15f5-4a37-405f-8e73-c5b57613b6cf)

## Scope
Review the R2 deliverables:
1. `api/workspace_intelligence.py`: Inspect `HBMunicipalURLIndex` and `EnvironmentalGISRadar`.
2. `api/main.py`: Inspect the null-safety fix at line 742, new endpoints `/api/workspace/hb-urls/stats`, `/api/workspace/hb-urls/search`, `/api/workspace/environmental/proximity`, `/api/workspace/gis/layers`, and `/api/genesis/ingest`.
3. `workspace_v2.html` and `templates/workspace_v2.html`: Verify 100% template parity, `#hb-urls-pane`, `#plume-pane`, and initial 5-node 4-edge Cytoscape topology.
4. Run:
   - `python -m unittest tests/test_workspace_intelligence.py`
   - `python -m unittest tests/test_genesis_ingest.py`
   - `python -m unittest tests/test_challenger1_genesis_hud_harness.py`
   - Parity check command: `python -c "assert open('workspace_v2.html', encoding='utf-8').read() == open('templates/workspace_v2.html', encoding='utf-8').read(); print('PARITY OK')"`
5. Render an explicit verdict: APPROVE or REQUEST_CHANGES.

Read:
- C:\OsintNeoAi\.agents\ORIGINAL_REQUEST.md
- C:\OsintNeoAi\AGENTS.md
- C:\OsintNeoAi\.agents\worker_impl_m1_m2\handoff.md

Write `report.md` and `handoff.md` with your verdict and findings, and message parent.

## 2026-09-10T19:09:08Z
You are reviewer_2.
Your working directory is C:\OsintNeoAi\.agents\reviewer_2.
Read C:\OsintNeoAi\.agents\ORIGINAL_REQUEST.md, C:\OsintNeoAi\AGENTS.md, and C:\OsintNeoAi\.agents\reviewer_2\DISPATCH.md.
Also read C:\OsintNeoAi\.agents\worker_impl_m1_m2\handoff.md.

Review R2 workspace intelligence engine (api/workspace_intelligence.py), API integration (api/main.py), and frontend parity (workspace_v2.html & templates/workspace_v2.html).
Run tests: python -m unittest tests/test_workspace_intelligence.py, python -m unittest tests/test_genesis_ingest.py, and python -m unittest tests/test_challenger1_genesis_hud_harness.py.
Write report.md and handoff.md with an explicit verdict (APPROVE or REQUEST_CHANGES).
Message parent with your findings.
