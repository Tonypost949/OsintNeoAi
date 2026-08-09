# RICO Enterprise Investigation — Canonical Briefing Exhibit
**Generated:** 2026-06-22 12:19:15 UTC
**Source:** BigQuery `noble-beanbag-497411-m4.ppp_rico` permanent views
**Scope:** Public record data only — PPP loans, property records, GeoTracker, IRS 990

---

## 1. Mercy House Board — PPP Self-Dealing Matrix

| Board Member | Vendor Entity | PPP Amount | Location | Legal Exposure |
|-------------|--------------|-----------|----------|----------------|
| MLADEN BUNTICH | Buntich Construction | $1,582,217 | Upland, CA | IRC 4941 Self-Dealing |
| BRYAN PAVALKO | RBA Builders LLC | $2,590,445 | Huntington Beach, CA | IRC 4941 Self-Dealing |
| MIA BERGMAN | Shopoff Realty Investments | $2,315,294 | Irvine, CA | IRC 4941 Self-Dealing |
| NATALIE MCCARTY | Shopoff Realty Investments | $2,315,294 | Irvine, CA | IRC 4941 Self-Dealing |
| **TOTAL** | **4 board members** | **$8,803,250** | **CA** | **IRC 4941** |

**Source:** `v_nonprofit_board_ppp_self_dealing` — Mercy House board members whose vendor companies received PPP.
**Document:** `meli-document-mercy-house-board-conflicts-of-interest (2).docx`

## 2. Out-of-State LLC Timing Matrix — Pre-Positioning Pattern

### Pattern A: Pre-Positioning (PPP approved BEFORE property acquisition)
| LLC | PPP Amount | Delta | PPP City | State | Mail City | Lender |
|-----|-----------|-------|----------|-------|-----------|--------|
| TRIUMVIRATE LLC | $852,740 | -275d | Anchorage | AK | FOUNTAIN VALLEY | Community Banks of Colorado, A |
| MNM GROUP LLC | $647,186 | -974d | LOS ANGELES | CA | VERNON | JPMorgan Chase Bank, National  |
| TRIUMVIRATE LLC | $619,100 | -589d | ANCHORAGE | AK | FOUNTAIN VALLEY | Community Banks of Colorado, A |
| STEWART INDUSTRIES LLC | $564,165 | -34d | Battle Creek | MI | SEAL BEACH | Bank of America, National Asso |
| STEWART INDUSTRIES LLC | $564,162 | -384d | BATTLE CREEK | MI | SEAL BEACH | Bank of America, National Asso |
| SWUN MATH LLC | $294,773 | -855d | CYPRESS | CA | CYPRESS | Farmers & Merchants Bank of Lo |
| EVERSTONE CAPITAL LLC | $146,499 | -1753d | NEW YORK | NY | NEWPORT COAST | PNC Bank, National Association |
| DBS-ENTERPRISES LLC | $131,908 | -806d | SANTA CLARA | CA | LAS VEGAS | Heritage Bank of Commerce |
| INFINITY PROPERTIES LLC | $93,200 | -1989d | MOUNDS | OK | NEWPORT BEACH | BancFirst |
| DBS-ENTERPRISES LLC | $78,694 | -793d | CAMDEN WYOMING | DE | LAS VEGAS | Wilmington Savings Fund Societ |

### Pattern B: Rapid Deployment (0-2 year delta)
| LLC | PPP Amount | Delta | PPP City | State | Mail City |
|-----|-----------|-------|----------|-------|-----------|
| COMPASSIONATE CARE HOSPICE LLC | $279,820 | +605d | FOUNTAIN VALLEY | CA | FOUNTAIN VALLEY |
| COMPASSIONATE CARE HOSPICE LLC | $279,820 | +605d | FOUNTAIN VALLEY | CA | FOUNTAIN VALLEY |
| THE LE FAMILY LLC | $213,900 | +595d | Killeen | TX | CORONA |
| HB LLC | $193,170 | +316d | PROVIDENCE | RI | EDMONDS |
| THE LE FAMILY LLC | $152,800 | +292d | KILLEEN | TX | CORONA |
| HB LLC | $146,130 | +618d | Long Beach | CA | EDMONDS |
| HB LLC | $105,100 | +310d | LONG BEACH | CA | EDMONDS |
| JJ HOLDINGS LLC | $102,390 | +148d | SHAKOPEE | MN | FRISCO |
| SDR LLC | $87,900 | +48d | LARAMIE | WY | ANAHEIM |
| SDR LLC | $69,600 | +26d | SOUTHLAKE | TX | ANAHEIM |

### Statistics
- Total LLCs matched: 112
- Total PPP rows: 275
- Out-of-state PPP: 223 (81%)
- Dual out-of-state (PPP + mail): 133

## 3. GeoTracker — HBNC Contamination Zone

| Site ID | Location | Contaminant | Level | Status |
|---------|----------|------------|-------|--------|
| HB-NAV-01 | Huntington Beach Navigation Center Footprint | Hexavalent Chromium (CrVI) | 49x regulatory limit | Disputed / Fraudulent Closure |
| HB-NAV-01 | HBNC Footprint | CrVI (Air) | Above OEHHA action level | Not remediated |
| HB-NAV-01 | HBNC Footprint | CrVI (Groundwater) | Migration confirmed | Not remediated |
| HB-NAV-01 | HBNC Footprint | Total Petroleum Hydrocarbons | Elevated | Not remediated |
| HB-NAV-01 | HBNC Footprint | Lead | Above 80 mg/kg | Not remediated |

**Source:** `national_audits.all_state_records` (CA), `geotracker.waterboards.ca.gov`
**Municipal awareness:** Jim Merid (City of HB) requested OCWD well data 03/11/2020 — 0.5 mile radius covering 17642 & 17472 Beach Blvd
**Adjacent source:** G&M Oil Co. #124 at 17472 Beach Blvd (Phase I ESA)

## 4. CMRA Mailbox Clusters (3+ LLCs)

| Mail Address | LLC Count | Avg Value | Risk Level | Notes |
|-------------|-----------|-----------|------------|-------|
| 11770 WARNER AVE STE 215 | 60 | $237,533 | CRITICAL | Major CMRA hub (60+ LLCs) |
| 220 NEWPORT CENTER DR # 11-557 | 57 | N/A | CRITICAL | Newport Center financial cluster |
| 3187 RED HILL AVE STE 213 | 38 | N/A | HIGH | None |
| 620 NEWPORT CENTER DR FL 11TH | 37 | $7,365,432 | HIGH | Newport Center financial cluster |
| 2161 VENTIA | 25 | N/A | HIGH | None |
| PO BOX 1549 | 24 | N/A | HIGH | USPS PO Box network |
| PO BOX 1368 | 21 | $1,327,500 | HIGH | USPS PO Box network |
| 17272 NEWHOPE ST | 20 | $980,000 | HIGH | Fountain Valley industrial cluster |
| 260 BAKER ST STE 100 | 20 | N/A | HIGH | None |
| 13070 OLD BOLSA CHICA RD | 20 | N/A | HIGH | None |

## 5. 7561 Center Ave Convergence Point

| LLC | Unit | Sale Price | Seller | Sale Date | Mail City |
|-----|------|-----------|--------|-----------|-----------|
| BROWN HUBERT LLC |  # D1 | N/A | CHEN, GEORGE T; CHEN, LEI | 04/29/2016 | HENDERSON |
| FREEDMAN ENTERPRISES LLC |  # G3 | N/A | FREEDMAN, CARL; FREEDMAN, | 12/31/2009 | HUNTINGTN BCH |
| KRS WERKS LLC |  # E1 | $825,000 | THOMAS, FLORA; THE THOMAS | 08/23/2023 | CERRITOS |
| DYLAN & ANDREW HOLDINGS L |  # J1 | $725,000 | PEREZ, MARCO V; GUADALUPE | 05/20/2022 | WESTMINSTER |

**Key:** DYLAN & ANDREW HOLDINGS LLC acquired unit J1 via $725K sale 05/20/2022 from PEREZ/GUADALUPE. CHEN seller on BROWN HUBERT LLC unit D1 — connects to Chen_Yamada supporting docs.
**ARPA nexus:** Tam Nguyen (Garden Grove Community Foundation) registered PPP out of Suite 45 — same complex.

## 6. Mercy House Living Centers — IRS 990 (FY2022)

| Metric | Amount |
|--------|--------|
| Revenue | $54,570,713 |
| Grants/Contributions | $53,239,888 |
| Total Assets | $27,817,685 |
| Total Liabilities | $17,836,905 |
| PPP Received | $1,339,000 (Paid in Full) |
| CEO Compensation (Larry Haynes) | $186,455 |

**Source:** Vertex AI OCR of 2022 990 PDF, ProPublica Nonprofit Explorer

## 7. Critical Timeline

| Date | Event |
|------|-------|
| 03/11/2020 | City of HB (Jim Merid) requests OCWD well data for 17631 Cameron / 17642 Beach (0.5 mile radius) |
| 08/21/2020 | OCHCA issues fraudulent Case Closed (20IC002) — certifies safety despite CrVI plume |
| 08/2020-01/2021 | City acquires Yamada parcel using $6,094,847 LMIHAF reserves |
| 05/04/2021 | STEWART INDUSTRIES LLC acquires 3311 Bounty Cir via 1077 PCH mailbox — 34 days after first PPP loan |
| 05/20/2022 | DYLAN & ANDREW HOLDINGS LLC acquires 7561 Center Ave #J1 for $725,000 |
| 2024 | CrVI soil sample: 490 ppb (49x EPA limit) |
| 2025 | Andrew Do sentenced to 5 years; $8.85M restitution default |

---
**Generated:** 2026-06-22 12:19:26 | **Project:** noble-beanbag-497411-m4 | **Dataset:** ppp_rico
**Data sources:** PPP (SBA), GeoTracker (CA Water Board), IRS 990 (ProPublica), OC Assessor (GIS), Phase I ESA (EEC Environmental)
