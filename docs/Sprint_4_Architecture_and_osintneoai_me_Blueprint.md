# Sprint 4 Architecture & osintneoai.me Production Deployment Blueprint

## 1. Domain & Infrastructure Overview: osintneoai.me

- **Primary Domain Target:** `https://osintneoai.me`
- **Subdomain Routing & DNS Mapping:**
  - `https://osintneoai.me` / `https://www.osintneoai.me` — Main Operational Workspace HUD (Clean Room UI, Floating Acrylic Chat, Cytoscape Maltego Graph)
  - `https://taxfunded.osintneoai.me` — Public Read-Only Ledger Explorer & Receipt Verification Terminal
  - `https://api.osintneoai.me` — Zero-Trust Append-Only Ingestion Webhook (Port 10001 / Cloud Run HTTPS)
  - `https://chronicle.osintneoai.me` — Franchise Newspaper Broadsheet & Daily Crypto Crossword Node

---

## 2. Sprint 4 Action Items (S12–S18)

### S12: Production Cloud Run Deployment & Custom Domain Binding (`osintneoai.me`)
- **Objective:** Containerize `dynamic_genesis_webhook.py` and the Flask backend using Docker and deploy to Google Cloud Run / Azure Container Apps.
- **Domain Binding:** Map CNAME and A/AAAA records for `osintneoai.me` and subdomains with managed TLS/SSL certificates.
- **WIF Authentication:** Configure Workload Identity Federation (WIF) for seamless GCP BigQuery ledger access without API key embedding.

### S13: Real-Time WebSockets & SSE Event Stream
- **Objective:** Implement Server-Sent Events (SSE) / WebSockets on `https://api.osintneoai.me/events` so that when a zero-value block is ingested or enriched by `bq_sync_worker.py`, the Workspace UI on `osintneoai.me` instantly flashes the receipt hash and updates the Cytoscape graph without page reloads.

### S14: Manifest V3 Browser Extension Node (`osintneoai.me` Webstore Integration)
- **Objective:** Package `C:\OsintNeoAi\chrome_extension\` into a Chrome Webstore release targeting `https://api.osintneoai.me/api/genesis/ingest`.
- **Functionality:** 1-click page scraping, point-of-upload client SHA-256 hashing, and immediate receipt generation directly from municipal/DTSC pages.

### S15: Municipal GIS Polygon Layer Overlay (Huntington Beach & Orange County)
- **Objective:** Integrate GeoJSON plume polygons for DTSC EnviroStor ID 30490016 (Ascon Landfill) and GeoTracker Case 20IC002 ($Cr\text{-VI}$ plume) into Cytoscape and Leaflet/Mapbox maps on `osintneoai.me`.

### S16: Automated Cal. CCP § 473(d) & Rule 60(d)(3) Court Filing Package Generator
- **Objective:** Build an automated PDF/Word legal document assembler that extracts user testimony, EDR contaminant data, and docket procedural flags to generate court-ready Notice of Motion and Motion to Vacate Void Judgment packages.

### S17: Tokenomics & Franchise Newspaper Micro-Subscriptions (50 TFT Reward Pool)
- **Objective:** Wire the TFT (TaxFunded Token) reward pool on `https://chronicle.osintneoai.me` to automatically credit users 50 TFT upon solving the daily forensic crossword or submitting corroborated municipal evidence.

### S18: Continuous System Reliability & Monitoring Sentinel
- **Objective:** Deploy `scripts/remote_vps_browser.py` daemon on `osintneoai.me` to monitor API uptime, BigQuery load job latency, and Gemini API rate limit quotas.

---

## 3. Architecture Topology

```
┌────────────────────────────────────────────────────────────────────────┐
│                        PUBLIC ACCESS LAYER                             │
├───────────────────────────────┬────────────────────────────────────────┤
│ https://osintneoai.me         │ Main Acrylic Workspace HUD             │
│ https://taxfunded.osintneoai.me│ Public Read-Only Ledger Explorer      │
│ https://chronicle.osintneoai.me│ Franchise Newspaper Broadsheet        │
└───────────────┬───────────────┴────────────────────┬───────────────────┘
                │                                    │
                ▼                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                 CLOUD RUN / API BACKEND LAYER                          │
│                   https://api.osintneoai.me                            │
│           (dynamic_genesis_webhook.py / Port 10001)                   │
└───────────────┬────────────────────────────────────┬───────────────────┘
                │                                    │
                ▼                                    ▼
┌────────────────────────────────┐  ┌──────────────────────────────────┐
│   BigQuery Append-Only Vault   │  │  Autonomous Enrichment Daemon    │
│  genesis_ledger (noble-beanbag)│  │      bq_sync_worker.py           │
└────────────────────────────────┘  └──────────────────────────────────┘
```
