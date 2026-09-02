# GenAI Blueprints 39 & 41 — TASK-016

Source: https://cloud.google.com/blog/products/ai-machine-learning/real-world-gen-ai-use-cases-with-technical-blueprints

## Blueprint 39 — Legal Document Extraction → OsintNeoAi
- **Use:** OC dockets `evidence/official_court_records/04_USA_v_Christopher_Ryan_...md` + `OC_Superior_Court_Case_30_2021_01201327_Full_ROA.md`
- **Pipeline:** `document-ai` `us` processor `ocr` → `vertex-ai` `gemini-2.5-flash` `AI.CLASSIFY` (`TASK-052 DONE`) → BigQuery `noble-beanbag-497411-m4` `forensic_layers` → Syncfusion grid `public/syncfusion_grid.html:7`
- **Demo:** `python cli/gcp_free_ai_demo.py --gemini` + `data/genai_blueprint_results.json`

## Blueprint 41 — Anti-Fraud AML Graph → OsintNeoAi
- **Use:** PPP $1.1M `data/nationwide_ppp_loan_fraud_enterprise_correlation.json` + provider graph `cli/data/graph.json:1` 2261 nodes/4077 edges
- **Pipeline:** `timesfm-2.5` `AI.DETECT_ANOMALIES` (`TASK-051 DONE`) → `VECTOR_SEARCH` `text-embedding-005` (`TASK-050 DONE`) → `public/gods_eye_view_max_data.html:1` 3D globe arcs
- **Action:** `https://osintneoai-app-949.azurewebsites.net/gods-eye-max` shows anomaly hotspots

*Both blueprints map to live Azure `opencode-ai-8609` gpt-5-mini + Gemini free tier.*
