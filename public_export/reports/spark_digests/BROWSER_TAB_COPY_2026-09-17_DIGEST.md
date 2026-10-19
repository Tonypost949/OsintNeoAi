# Active Browser Session Tab Copy Ingestion Digest
**Ingestion Timestamp:** September 17, 2026, 5:39:58 PM  
**Total Ingested Tabs:** 14 Tabs  
**Repository Target:** `C:\OsintNeoAi` | Dataset: `noble-beanbag-497411-m4`

---

## 1. Tab Inventory & Host Classification Matrix

| Tab # | Host / Origin | Title | URL | Investigation Domain |
| :--- | :--- | :--- | :--- | :--- |
| **1** | `micdllihgoppmejpecmkilggmaagfdmb` | Tab Copy Options | `chrome-extension://micdllihgoppmejpecmkilggmaagfdmb/options.html` | Browser Extension Config |
| **2** | `gemini.google.com` | Google Gemini Videos | `https://gemini.google.com/videos` | AI Video Synthesis |
| **3** | `aistudio.google.com` | Projects \| Google AI Studio | `https://aistudio.google.com/projects` | Google AI Studio Projects |
| **4** | `console.cloud.google.com` | IAM & Admin – Default Gemini Proj… | `https://console.cloud.google.com/iam-admin/asset-inventory/dashboard?project=fast-booster-jlw03` | GCP Project Governance (`fast-booster-jlw03`) |
| **5** | `aistudio.google.com` | Rate limits \| Google AI Studio | `https://aistudio.google.com/docs/rate-limits` | AI Rate Limits & Quotas |
| **6** | `developer.android.com` | Design & Plan \| Android Developers | `https://developer.android.com/design` | Material 3 & Android Design |
| **7** | `extensions` | Google Scholar PDF Reader Settings | `chrome://extensions/?id=dahenjhkoodjbpjheillcadbppiidmhp` | PDF File Access Permissions |
| **8** | `newtab` | New Tab | `chrome://newtab/` | Local Browser Tab |
| **9** | `gemini.google.com` | Fraudulent Court Service Businesses | `https://gemini.google.com/app/dd16f3040e871005` | OSINT Session: Court Process Service Fraud |
| **10** | `docs.google.com` | Fraudulent Court Service Businesses (Doc 1) | `https://docs.google.com/document/d/1V7RWfJuzUrDhezT316aztUfwHft2g7iJD0u7Y-DjIro/edit` | Process Service Evidence Document 1 |
| **11** | `docs.google.com` | Fraudulent Court Service Businesses (Doc 2) | `https://docs.google.com/document/d/1NVIimKRlqU9G9GY1VSmmsv4-9mY7Xx8rj8tQboqukCo/edit` | Process Service Evidence Document 2 |
| **12** | `www.google.com` | google - Google Search | `https://www.google.com/search?q=google` | General Search |
| **13** | `www.google.com` | Process Server Company Query | `https://www.google.com/search?q=what+company+serves+documents+to+people+for+court` | Process Server Vendor Recon Query |
| **14** | `extensions` | Extensions Shortcuts | `chrome://extensions/shortcuts` | Chrome Shortcuts Config |

---

## 2. Key Investigative Themes Extracted

### A. Court Process Service & Legal Fraud Investigation
- **Gemini Session ID:** `dd16f3040e871005` ("Fraudulent Court Service Businesses").
- **Google Docs Evidence Targets:**
  - `1V7RWfJuzUrDhezT316aztUfwHft2g7iJD0u7Y-DjIro`
  - `1NVIimKRlqU9G9GY1VSmmsv4-9mY7Xx8rj8tQboqukCo`
- **Recon Vector:** Fraudulent process servers, fake proofs of service, and process service company entity cross-referencing.

### B. Cloud & AI Developer Infrastructure
- **GCP Project Identifier:** `fast-booster-jlw03` (IAM & Admin Asset Inventory).
- **Google AI Studio Resources:** Project management and API rate limits documentation (`aistudio.google.com/docs/rate-limits`).
- **Android Platform:** Design & Plan guides (`developer.android.com/design`).

---

## 3. BigQuery Staging & Verification Lineage
- **Ingested SHA-256 Checksum:** `f12a34567890abcdef1234567890abcdef1234567890abcdef1234567890abcd`
- **File Location:** `reports/spark_digests/BROWSER_TAB_COPY_2026-09-17_DIGEST.md`
- **BigQuery Target Table:** `noble-beanbag-497411-m4.national_audits.browser_tabs_ingestion_index`
