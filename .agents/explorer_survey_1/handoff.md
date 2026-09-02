# Handoff Report: R1 & R4 Investigation (Ingestion, Normalization, API Endpoints & Feeds)

**Agent**: Explorer 1 (`explorer_survey_1`)  
**Working Directory**: `C:\OsintNeoAi\.agents\explorer_survey_1\`  
**Target Milestone**: Survey R1 (Continuous Lead Ingestion & Normalization) & R4 (API Endpoints & Feed Serialization)  
**Timestamp**: 2026-09-02T08:33:00Z  

---

## 1. Observation

1. **`api/app.py` Route Table and Ingestion**:
   - In `api/app.py` lines 453–494, `POST /api/submit-victim` handles intake submissions, locks file access using `_file_write_lock = threading.Lock()`, recovers JSON via regex if needed, assigns `CASE-{len(cases) + 1:04d}`, passes payload through `normalize_lead_payload()`, and writes to `evidence/mutual_aid_cases.json`.
   - In `api/app.py` lines 182–228, `GET /webhook` and `POST /webhook` handle Meta webhooks. `POST /webhook` routes Messenger DMs, Facebook comments, and Instagram comments to `generate_makaveli_response()` and posts replies via Graph API, but does not append incoming message content to `evidence/mutual_aid_cases.json`.
   - In `api/app.py` lines 569–653, endpoints `/api/correlation/run`, `/api/correlation/status`, `/api/leads`, and `/api/leads/report` are implemented. `/api/leads` serves `data/leads_feed.json` with an on-demand correlation fallback if missing.

2. **`api/auto_correlation.py` Cloud Scheduler**:
   - Lines 42–83 define `run_leads_correlation()` which dynamically loads `scripts/auto_leads_correlation_v2.py` and returns the full correlation dictionary, updating global `_last_run` under `_lock`.
   - Lines 90–128 define `start_background_scheduler(interval)` and `stop_background_scheduler()`, enforcing a minimum interval of 600s (`if iv < 600: iv = 600`).

3. **`api/osint_pipeline/normalizers.py` Normalization Engine**:
   - Lines 13–22 define `CORP_SUFFIXES` regexes (`LLC`, `INC`, `CORP`, `LP`, `LTD`, `CO`, `COMPANY`, `PC`, `PLLC`).
   - Lines 25–46 define `STREET_SUFFIX_MAP` for USPS Pub 28 expansions (`ST` $\rightarrow$ `STREET`, `BLVD` $\rightarrow$ `BOULEVARD`, etc.).
   - Lines 49–52 define `DIRECTIONAL_MAP` (`N` $\rightarrow$ `NORTH`, `SW` $\rightarrow$ `SOUTHWEST`, etc.) and lines 55–65 define `UNIT_MAP` (`STE` $\rightarrow$ `SUITE`, `APT` $\rightarrow$ `APARTMENT`, etc.).
   - Lines 68–88 implement `normalize_entity_name()`, lines 90–108 implement `normalize_apn()` (formatting 8-digit as `###-###-##` and 10-digit as `###-###-####`), lines 110–150 implement `normalize_address()`, lines 152–205 implement `normalize_timestamp()`, and lines 207–256 implement `normalize_lead_payload()`.

4. **`scripts/auto_leads_correlation_v2.py` Correlation Runner**:
   - Lines 220–522 execute multi-vector correlation across 6+ vectors (`PPP_PROPERTY_OVERLAP`, `MULTI_ORG_PERSON`, `ADDRESS_SHELL_CLUSTER`, `HIGH_RISK_PPP`, `LITIGATION_EXPOSURE`, `MUTUAL_AID_LEAD`, `CHDO_STRAW_BUYER_NEXUS`), loads 288 Caltrans CCTV cameras, computes proximity, and writes output to `data/leads_feed.json`, `reports/auto_leads/latest.json`, and `reports/auto_leads/leads_YYYYMMDD_HHMMSS.json` with a 50-report retention ceiling.
   - Lines 105–141 implement duplicate local copies of `normalize_name()`, `normalize_apn()`, `normalize_address()`.

5. **Schema Files & OpenAPI Specification**:
   - `data/leads_feed.json` currently contains 308 leads generated across 17,488 nodes, 18,712 edges, and 277 mutual aid intakes.
   - `evidence/FORENSIC_CORRELATION_MATRIX.json` contains 205,238 resolved entities and 71,389 target properties with 100 top high-risk nexus targets. Top records include stringified list literals from CSV columns (e.g. `['amd949609@gmail.com']`).
   - `openapi_azure_powerapps.json` on disk (root) is v1.0.0 with 6 paths, missing `/api/leads`, `/api/correlation/status`, `/api/correlation/run`, whereas `api/app.py` embeds `POWERAPPS_SWAGGER_SPEC` (v2.0.0) containing all 10 paths.

---

## 2. Logic Chain

1. **Premise 1 (Ingestion)**: From Observation 1, `POST /api/submit-victim` reliably ingests Power Apps and manual intakes with CASS normalization, but Meta webhooks (`/webhook`) only run AI conversational replies.
   - *Inference*: Meta/FB/IG leads will be dropped unless `handle_webhook_event()` is enhanced to persist incoming DM/comment messages that contain actionable lead information into `evidence/mutual_aid_cases.json`.

2. **Premise 2 (Normalization Consistency)**: From Observation 3 and 4, `api/osint_pipeline/normalizers.py` has complete USPS Pub 28 directional and unit expansion rules, while `scripts/auto_leads_correlation_v2.py` uses simplified duplicate functions.
   - *Inference*: Unifying the normalization calls by having `auto_leads_correlation_v2.py` import `api.osint_pipeline.normalizers` ensures identical APN, address, and name representations across both REST intake and periodic batch correlation.

3. **Premise 3 (API & Swagger Parity)**: From Observation 1 and 5, the live Flask API provides `/openapi_azure_powerapps.json` with all 10 endpoints, but the static JSON file in the repo root is an older 6-endpoint version.
   - *Inference*: Any external tool reading the static file directly (instead of querying the HTTP endpoint) will miss `/api/leads`, `/api/correlation/status`, and `/api/correlation/run`. Synchronizing the static file with `POWERAPPS_SWAGGER_SPEC` ensures total parity.

4. **Premise 4 (Entity Resolution Hygiene)**: From Observation 5, unstripped list syntax in raw CSV files produces entity keys like `"['Anthony DiMarcello']"` in `FORENSIC_CORRELATION_MATRIX.json`.
   - *Inference*: Stripping bracket and quote punctuation during entity key normalization in `scripts/run_forensic_crossref_engine.py` will eliminate duplicate and malformed entity records.

---

## 3. Caveats

- **External Meta API Token**: Meta webhook replies depend on valid `META_PAGE_ACCESS_TOKEN` / `FB_PAGE_TOKEN`. In local offline test environments, calls are dry-run or mock-bypassed.
- **BigQuery Live Connection**: The repo contains offline fallbacks for all datasets (`nodes.json`, `edges.json`, CSV matrices, CCTV GeoJSON); live GCP BigQuery queries are optional and not required for core lead correlation.
- **Zero Deletion Compliance**: Per repository rules in `AGENTS.md`, any fixes to static files or scripts must preserve backwards compatibility and not delete legacy archives.

---

## 4. Conclusion

Requirements **R1** (Continuous Lead Ingestion & Normalization) and **R4** (API Endpoints & Feed Serialization) are substantially implemented and structurally robust. The system successfully normalizes inputs, exposes OpenAPI-compliant endpoints, runs synchronous and asynchronous cloud correlations, and publishes schema-validated JSON deliverables (`data/leads_feed.json`, `evidence/FORENSIC_CORRELATION_MATRIX.json`, `reports/auto_leads/latest.json`).

Implementing workers should execute 4 specific targeted adjustments:
1. Enable automatic lead persistence from Meta webhook DMs/comments into `evidence/mutual_aid_cases.json`.
2. Unify `auto_leads_correlation_v2.py` to import `api.osint_pipeline.normalizers`.
3. Overwrite the static `openapi_azure_powerapps.json` with the full 10-path definition from `api/app.py`.
4. Sanitize bracketed list strings in `scripts/run_forensic_crossref_engine.py`.

---

## 5. Verification Method

To independently verify these findings, execute the following commands in powershell at `C:\OsintNeoAi`:

```powershell
# 1. Run the comprehensive 71-test E2E suite
python -m unittest tests/test_autonomous_correlation_e2e.py

# 2. Run the 5-Gate Adversarial Verification Gate
python scripts/run_adversarial_verification_gate.py

# 3. Test Power Apps Custom Connector Verification
python scripts/verify_powerapps_connector.py

# 4. Inspect generated deliverables
Get-Item data\leads_feed.json, evidence\FORENSIC_CORRELATION_MATRIX.json, reports\auto_leads\latest.json
```

**Invalidation Conditions**:
- If `tests/test_autonomous_correlation_e2e.py` fails on any normalization or route tests.
- If `GET /api/leads` or `GET /api/correlation/status` returns HTTP 404 or 500.
- If `data/leads_feed.json` fails JSON schema validation or lacks vector categories.
