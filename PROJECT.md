# Project: OsintNeoAi 24/7 Autonomous Forensic Correlation & Lead Matching Pipeline

## Architecture
The system provides a continuous, cloud-native forensic correlation and lead matching engine hosted in Microsoft Azure App Service, backed by a 17,488-node / 18,712-edge topological knowledge graph, 288 Caltrans CCTV cameras, and 71 deep forensic datasets (196,780 records across 205,238 resolved entities).

```
[Inflow Sources: Power Apps Forms / Meta DMs / Webhooks / Mutual Aid]
                               │
                               ▼
           [Normalization Engine (USPS Pub 28, APN, CASS)]
                               │
                               ▼
        [Topological Graph Cross-Referencer & CCTV Proximity]
       (17.4k Active Graph + 71 Datasets + 288 Caltrans CCTVs)
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
 [Cloud Background Scheduler]          [Multi-Channel Feeds & APIs]
 (Azure 2h daemon + /run?async=1)       (/api/leads, /api/correlation/status,
                                        leads_feed.json, matrix, Power Apps)
```

## Feature Inventory
| # | Feature | Description | Milestone | Source | Status |
|---|---------|-------------|-----------|--------|--------|
| 1 | Lead Ingestion & Webhook Intake | Ingest Power Apps, Meta DMs, Webhooks into `evidence/mutual_aid_cases.json` | M1 | Survey / R1 | VERIFIED |
| 2 | CASS & USPS Pub 28 Normalization | Canonical entity names, APNs (8/10-digit), addresses, ISO 8601 timestamps | M1 | Survey / R1 | VERIFIED |
| 3 | Topological Graph Traversal | Cross-reference against 17.4k node graph & 71 forensic datasets across 6+ vectors | M2 | Survey / R2 | VERIFIED |
| 4 | 288 Caltrans CCTV Proximity | Haversine distance geocoding to 288 cameras with stream/snapshot metadata | M2 | Survey / R2 | VERIFIED |
| 5 | Cloud Scheduler & Async REST Trigger | Azure App Service 2-hour daemon, `/api/correlation/run?async=1`, zero local load | M3 | Survey / R3 | VERIFIED |
| 6 | Multi-Channel Alert & Feed Serialization | Output `data/leads_feed.json`, `evidence/FORENSIC_CORRELATION_MATRIX.json`, `/api/leads` | M4 | Survey / R4 | VERIFIED |
| 7 | Power Apps Connector & Dashboard Contracts | OpenAPI 2.0 Swagger spec, CORS `*`, Syncfusion grid & God's Eye View feeds | M4 | Survey / R4 | VERIFIED |
| 8 | 5-Gate Adversarial & 71-Test E2E Suite | 100% compliance across Code Quality, Cloud Contracts, Spatial, Concurrency, Forensics | M5 | Survey / Acceptance | VERIFIED |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Lead Ingestion & Normalization Engine | `api/app.py`, `api/osint_pipeline/normalizers.py`, Webhooks | none | DONE |
| M2 | Graph Cross-Referencing & CCTV Proximity | `scripts/run_forensic_crossref_engine.py`, `scripts/calculate_cctv_proximity.py`, `scripts/auto_leads_correlation_v2.py` | M1 | DONE |
| M3 | Cloud Background Scheduler & REST Controller | `api/auto_correlation.py`, Azure startup hooks, `POST /api/correlation/run` | M1, M2 | DONE |
| M4 | Feed Serialization & Power Apps Integration | `data/leads_feed.json`, `evidence/FORENSIC_CORRELATION_MATRIX.json`, `scripts/verify_powerapps_connector.py` | M2, M3 | DONE |
| M5 | 5-Gate Adversarial Verification & 3-Way Backup | `scripts/run_adversarial_verification_gate.py`, `tests/test_autonomous_correlation_e2e.py`, 3-Location Backup | M1, M2, M3, M4 | DONE |

## Interface Contracts
### Ingestion ↔ Normalization
- `normalize_lead_payload(raw_dict) -> dict`: Returns canonicalized payload with `normalized_name`, `normalized_apn`, `normalized_address`, `normalized_timestamp`, and `geo_anchor`.

### Normalization ↔ Graph Traversal
- `run_leads_correlation() -> dict`: Executes multi-vector topological graph matching across `nodes.json` and `edges.json`, matches against CCTV cameras from `public/caltrans_d12_cctv.geojson`, serializes `data/leads_feed.json` and `reports/auto_leads/latest.json`.

### Scheduler ↔ API Endpoints
- `GET /api/correlation/status`: Returns JSON telemetry `{ "auto_correlation_available": bool, "scheduler_running": bool, "last_run": dict, "total_leads": int }`.
- `POST /api/correlation/run?async=1`: Triggers non-blocking background thread and immediately returns HTTP 200 `{"status": "triggered", "mode": "async"}` in <35ms.
- `GET /api/leads`: Serves JSON array of active leads with dynamic on-demand fallback.

## Code Layout
- `api/app.py`: Flask API entrypoint, Webhook listeners, Power Apps endpoints.
- `api/auto_correlation.py`: Background thread scheduler and correlation invoker.
- `api/osint_pipeline/normalizers.py`: CASS address/APN/entity normalizers.
- `scripts/auto_leads_correlation_v2.py`: Multi-vector graph correlation engine.
- `scripts/calculate_cctv_proximity.py`: 288 Caltrans CCTV proximity calculator.
- `scripts/run_forensic_crossref_engine.py`: Master CSV matrix cross-reference compiler.
- `scripts/run_adversarial_verification_gate.py`: 5-Gate Master Verification Harness.
- `scripts/verify_powerapps_connector.py`: Power Apps Custom Connector verification.
- `tests/test_autonomous_correlation_e2e.py`: 71-test E2E verification suite.
- `evidence/FORENSIC_CORRELATION_MATRIX.json`: Master cross-reference matrix.
- `data/leads_feed.json`: Live correlation feed.
- `public/caltrans_d12_cctv.geojson`: 288 CCTV camera definitions.
