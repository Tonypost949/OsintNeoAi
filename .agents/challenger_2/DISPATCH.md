# Dispatch Instructions for challenger_2

## Identity & Role
- Role: Empirical Data & Spatial Integrity Challenger
- Archetype: teamwork_preview_challenger
- Working directory: C:\OsintNeoAi\.agents\challenger_2
- Parent: orchestrator_13 (e68e15f5-4a37-405f-8e73-c5b57613b6cf)

## Scope
Perform empirical verification of data integrity and spatial computations:
1. Verify the 82,757 municipal URLs dataset integrity:
   - Count lines and unique URLs in `data/hb_urls_master.txt`.
   - Verify category distribution in `data/neo_hb_urls_forensic_classification.json`.
   - Benchmark in-memory search latency across 1,000 rapid queries.
2. Verify GeoTracker UST and Cameron Lane GIS data integrity:
   - Verify 15,847 records in `opencode_work/geotracker/permitted_ust.txt`.
   - Verify Haversine distance accuracy against known ground-truth coordinates (e.g., HB City Hall, Cameron Lane, Ascon Superfund).
   - Verify that the -85% toxic stigma discount and legal remedies are accurately attributed when inside the contamination plume.
3. Write an empirical test script and execute it.
4. Render an explicit verdict: APPROVE or REJECT.

Read:
- C:\OsintNeoAi\.agents\ORIGINAL_REQUEST.md
- C:\OsintNeoAi\AGENTS.md
- C:\OsintNeoAi\.agents\worker_impl_m1_m2\handoff.md

Write `report.md` and `handoff.md` with your verdict and findings, and message parent.

## 2026-09-10T19:09:08Z
Empirically verify the data integrity and spatial computations of the 82,757 municipal URLs and DTSC/GeoTracker GIS datasets.
Benchmark search performance, verify Haversine distance accuracy, and check toxic stigma calculations.
Write an empirical verification script, execute it, and record results.
Write report.md and handoff.md with an explicit verdict (APPROVE or REJECT).
Message parent with your findings.
