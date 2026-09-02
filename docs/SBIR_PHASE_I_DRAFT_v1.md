# SBIR/STTR Phase I — Dual-Use Automated RegTech & OSINT Forensic Intelligence (TASK-002)

**Agency Fit:** NSF 24-527 (Data & AI) + DoD AFWERX Open Topic 24.3 (Digital Engineering) — non-dilutive $275k Phase I, 6 months.

## 1. Technical Innovation (OSINTNeoAi as-a-Service)
- **Problem:** 10,000+ California agencies manually audit CEQA AB52, NAHC Sacred Lands, Surplus Land Act §54220, and PPP fraud with 0 unified graph.
- **Solution:** `data/tasks.json:38` 52-task autonomous engine + `cli/data/graph.json` 2261 nodes/4077 edges + BigQuery `noble-beanbag-497411-m4` + `public/syncfusion_grid.html:7` forensic ledger + `public/gods_eye_view_max_data.html:1` 3D globe. Auto-ingests 288 Caltrans CCTV `public/caltrans_d12_cctv.geojson` + 50 municipal `public/data/municipal_matrix.json` + 115.8M counterfeit pills `data/nationwide_counterfeit_prescription_correlation.json`.
- **Phase I Work:** 
  - T1: Fine-tune `text-embedding-005` + `gemini-2.5-flash` `AI.CLASSIFY` over OC dockets (`TASK-050/052 DONE`)
  - T2: TimesFM 2.5 anomaly over `forensic_layers.ppp_loans` (`TASK-051 DONE`)
  - T3: Syncfusion PDF/Excel export + Power Apps connector `openapi_azure_powerapps.json`

## 2. Commercialization
- **Beachhead:** Environmental law firms (CEQA compliance) at $500/mo `TASK-009` — 200 firms x $6k = $1.2M ARR.
- **Dual-Use:** DoD installation resilience + municipal procurement fraud.
- **Pipeline:** SCORE `https://www.score.org` (TASK-001) + SBDC Orange County review.

## 3. Team & Facilities
- PI: Anthony DiMarcello (Post University Entra `anthony.dimarcello@students.post.edu`), Azure `opencode-ai-8609` `gpt-5-mini/gpt-4.1-mini` `https://opencode-ai-8609-a7f40.openai.azure.com/`
- Infra: `https://osintneoai-app-949.azurewebsites.net` B1 East US (free $100/mo students), `https://dev.azure.com/anthonydimarcello` `mcp.dev.azure.com/anthonydimarcello`

## 4. Budget (6 mo)
- Personnel 60% $165k, Cloud $15k (BigQuery/Gemini free tier + Azure), Travel $5k (SCORE), Indirect 30%.

## 5. Submission Checklist
- [ ] Register SAM.gov + SBIR.gov topics
- [ ] Attach `docs/POST_UNIVERSITY_LIBRARY_STUDY_GUIDE.md` + `legal_library/INDIGENOUS_TRIBAL_LAND_RIGHTS_AND_CULTURAL_RESOURCES_AUDIT.md` as appendices
- [ ] Demo links: `/syncfusion` `/gods-eye-max` `/api/tasks`

*Generated 2026-09-01 for TASK-002 — copy to `https://www.sbir.gov` submission portal.*
