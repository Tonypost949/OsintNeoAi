# Huntington Beach City – Infrastructure Report (as of 2026‑06‑16)

## Executive Summary
The City of Huntington Beach hosts a hybrid web architecture. Public‑facing marketing and CMS sites are protected by Cloudflare’s CDN/WAF, while legacy data services (Laserfiche records repository and ESRI ArcGIS mapping) are exposed on the city‑owned IP block **192.5.222.0/24** (ASN **393281**). This creates a critical “Swiss‑cheese” exposure where sensitive environmental and permitting data can be accessed without WAF protection.

---

## 1. DNS & IP Mapping
| Subdomain | Record Type | IP Address(es) | ASN | Org / Provider | WAF / Protection | Exposure Level |
|---|---|---|---|---|---|---|
| `huntingtonbeachca.gov` | A | 104.26.15.40, 104.26.14.40, 172.67.68.156 | 13335 | Cloudflare Inc. | Cloudflare WAF (edge) | Medium |
| `www.huntingtonbeachca.gov` | A | 104.26.15.40, 104.26.14.40, 172.67.68.156 | 13335 | Cloudflare Inc. | Cloudflare WAF (edge) | Medium |
| `cms3.revize.com` | A | 104.20.47.216, 172.66.151.167 | 13335 | Cloudflare Inc. | Cloudflare WAF (edge) | Medium |
| `gis.huntingtonbeachca.gov` | A | 192.5.222.153 | **393281** | **City of Huntington Beach** | **None (direct)** | **Critical** |
| `records.huntingtonbeachca.gov` | A | 192.5.222.218 | **393281** | **City of Huntington Beach** | **None (direct)** | **Critical** |
| `permit.huntingtonbeachca.gov` | NXDOMAIN | – | – | – | Dead / not in DNS | Low |

*The two critical IPs belong to the city‑owned subnet 192.5.222.0/24, indicating on‑premise hosting.*

---

## 2. Service Fingerprinting (Publicly Available Information)
| Host (IP) | Observable Services (public sources) | Application |
|---|---|---|
| **192.5.222.153** | HTTPS (443) – likely ESRI ArcGIS Server (`/arcgis/rest/services`) | GIS mapping / spatial data portal |
| **192.5.222.218** | HTTPS (443) – likely Laserfiche Web Client (`/WebLink/DocView.aspx`) | Document management / records repository |

*No Cloudflare proxy sits between the client and these services; the TLS certificates presented are the server‑owned certificates.*

---

## 3. Architectural Overview
```mermaid
graph LR
    subgraph Public Front‑End
        A[Root Domain & www] -->|Cloudflare CDN/WAF| CF[Cloudflare Edge]
        B[cms3.revize.com] -->|Cloudflare CDN/WAF| CF
    end
    subgraph On‑Premise Services
        C[gis.huntingtonbeachca.gov] -->|Direct IP| GIS[ArcGIS Server (192.5.222.153)]
        D[records.huntingtonbeachca.gov] -->|Direct IP| LF[Laserfiche (192.5.222.218)]
    end
    CF -.->|Origin (not disclosed)| Origin[City Origin Servers]
    style Public Front‑End fill:#e3f2fd,stroke:#2196f3,stroke-width:2px
    style On‑Premise Services fill:#ffebee,stroke:#f44336,stroke-width:2px
```
*The diagram highlights the split between edge‑protected services and the exposed on‑premise layer.*

---

## 4. Risk Assessment
| Asset | Confidentiality Impact | Integrity Impact | Availability Impact | Likelihood (based on exposure) |
|---|---|---|---|---|
| **ArcGIS (`gis.`)** | **High** – contains parcel maps, zoning layers, environmental overlays. | **Medium‑High** – unauthorized edits could corrupt spatial data. | **Low‑Medium** – service appears publicly reachable; DoS is possible. | **High** – no WAF, direct IP.
| **Laserfiche (`records.`)** | **High** – stores environmental permits, inspection reports, FOIA filings. | **Medium** – IDOR could expose internal documents. | **Low‑Medium** – service reachable over HTTPS; can be throttled. | **High** – direct exposure.
| **Public Web (`www` / root)** | **Low** – marketing content. | **Low** – static pages. | **Low** – Cloudflare mitigates.
| **Revize CMS (`cms3.revize.com`)** | **Medium** – may host static PDFs. | **Medium** – if mis‑configured, can leak drafts. | **Low** – Cloudflare protects.

---

## 5. Recommendations (Defensive)
1. **Move legacy services behind a reverse‑proxy/WAF** – Deploy Cloudflare Spectrum or an on‑premise reverse proxy to terminate TLS and enforce rate‑limiting.
2. **Restrict ArcGIS and Laserfiche to authenticated IP ranges** – Use firewall ACLs to allow only internal staff VPN subnets.
3. **Upgrade to the latest supported ESRI and Laserfiche versions** – Patch known CVEs (e.g., CVE‑2023‑XXXXX for ArcGIS services, CVE‑2022‑XXXXX for Laserfiche).
4. **Implement strict SAML/OIDC authentication** – Ensure all document access requires multi‑factor authentication.
5. **Enable logging and anomaly detection** – Capture request patterns on the exposed IPs; trigger alerts on bulk IDOR‑style traffic.
6. **Consider consolidating to a SaaS platform** – Migrating permits and records to a managed solution (e.g., Accela, Tyler) reduces on‑premise exposure.

---

## 6. Sources & Enrichment
- PowerShell `Resolve‑DnsName` output (June 2026) for DNS → IP mapping.
- ASN lookup confirming **393281** → “City of Huntington Beach”.
- Public Shodan/Censys snapshots (retrieved via web search) showing the service banners for the two critical IPs.
- City‑issued building permit C81252 (Standard Oil Tract 405) providing background on the environmental context.

---

*Prepared by the OSINT agent for internal use. All data reflects publicly observable information as of 2026‑06‑16; any further reconnaissance should comply with applicable laws and organizational policies.*
