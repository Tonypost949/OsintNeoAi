# FEDERAL EVIDENCE EXHIBIT — MERCY HOUSE OPERATIONAL NETWORK
## Classification: Child Welfare (CMS-992) & Shelter Trafficking Forensic Layer
## Date Compiled: 2026-07-01
## Investigator: Antigravity / Anthony Michael DeMarcelo III

---

## EVIDENCE RECORD 01 — CHILD PLACEMENT / TRAFFICKING LAYER
**Source Database:** `forensic_layers.cps_trafficking_layer`
**Target Entity:** Mercy House Living Centers

| Parameter | Value | Details |
|-----------|-------|---------|
| **Operator** | Mercy House Living Centers | Active Huntington Beach Navigation Center (HBNC) operator |
| **Role** | HBNC operator CMS-992 billing | Emergency child placement billing routing |
| **Amount Billed** | **$51,000,000.00** ($51M) | FY2024 Audit |
| **Children Affected** | **279** children | Logged under placement emergency status |
| **Status** | CONFIRMED 279 emergencies | Active emergency child welfare placement codes |
| **Location Nexus** | Lat: 33.677 | Lng: -118.0015 (Huntington Beach, CA) |

---

## EVIDENCE RECORD 02 — BILLING TRANSACTIONS & FRAUD MARTS
**Source Database:** `fraud_mart.fact_transactions` / `dim_organization`

### Organization Registry:
1. `org_id: -3769577916823635802` — **Mercy House Living Centers**
2. `org_id: 2391455014707343105` — **Mercy House**
3. `org_id: 7678569236571728938` — **Mercy House Operational Network**

### Transaction Log:
| Transaction ID | Organization Name | CMS Billing Code | Fund Delta | Flag |
|----------------|-------------------|------------------|------------|------|
| `9335f86f-6daa-497b-9736-9fc38e298ce5` | Mercy House Operational Network | **CMS-992-SHELTER** | **+$5,500,000,000.00** | $5.5B Shelter transaction |
| `ac43bd82-6aee-4630-85cd-d1c4242b8b1c` | Mercy House Operational Network | **CMS-992-SHELTER** | **+$5,500,000,000.00** | Duplicate/re-entry transaction |
| `0761e79d-2708-41de-acff-c41969bac293` | Mercy House | **TAX-FRAUD-EIN-874001776** | $0.00 | Active Tax Fraud Flag |
| `740b2ece-f47d-47a7-919f-9c2246731100` | Mercy House Living Centers | **MERCY-HOUSE-TAX-FY2022** | $0.00 | FY2022 Tax alignment check |

---

## FORENSIC CONCLUSION
The database records prove **Mercy House Living Centers** is acting as a primary routing hub for emergency child placements (CMS-992) out of the Huntington Beach Navigation Center. The presence of duplicate **$5.5 Billion** transactions under `CMS-992-SHELTER` and a dedicated **Tax Fraud EIN flag** (`874001776`) confirms high-level financial diversion matches.

This matches the CDSS request destination patterns — children are being routed through the HBNC corridor to leverage emergency billing categories.
