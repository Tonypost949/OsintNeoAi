# Mercy House + CHDO Financial Cross-Reference Summary
**Generated: 2026-06-20**

---

## 1. CHDO TRANSACTIONS (from Mercy House Audit)

| CHDO Entity | Project | Transaction Type | Amount | Counterparty | Key Notes |
|---|---|---|---|---|---|
| Casa Aliento Mercy House CHDO LLC | Vagabond Inn (Oxnard) | Real Estate Sale | $15,000,000 | Casa Aliento LP | Sold Sept 2023; $1.5M Century note + $13.5M seller carryback |
| Mercy House Living Centers (via CHDO) | Vagabond Inn | Note Receivable | $13,500,000 | Casa Aliento LP | 4.19%, 55yr, principal & interest DEFERRED; ~$443K accrued interest |
| CM Mercy House CHDO LLC | Mesa Vista (Costa Mesa) | Ground Lease | — | County of Orange | 55-year lease; Century note funded operating right-of-use |
| CM Mercy House CHDO LLC | Mesa Vista | Note Payable | $7,900,000 | Century Housing Corp | SOFR+4.75% floor 7.50%; Paid down $6.5M Feb 2024 with COUNTY GRANT funds |
| CM Mercy House CHDO LLC | Mesa Vista | Note Payable | $2,000,000 | Government Agency | 3%, 55yr; subordinate public financing |
| CM Mercy House CHDO LLC | Mesa Vista | Grant | $1,457,000 | City of Costa Mesa | FY2024 (plus $2.04M in FY2023) |
| 2nd and B Mercy House CHDO LLC | 2nd & B Shelter (Oxnard) | Note Payable | $4,399,210 | City of Oxnard Housing Dept | 0%, 15yr; ONLY 10% ($439,921) DRAWN as of June 30 2024 |
| Mercy House CHDO Inc. | Vagabond Inn | Note Payable | $1,500,000 | Century Housing Corp | Paid off Sept 18 2023 from Casa Aliento sale proceeds |
| Mercy House Living Centers | Kraemer Place Shelter | Operating Lease | $0 | County of Orange | No rent; fair value ~$109K/yr recorded as in-kind |
| Mercy House Living Centers | Board of Directors | Contributions | $303,000 | Members of Board | FY2024; $125K in FY2023 — RELATED-PARTY FUNDING |

---

## 2. PPP MATCHES

### Direct Entity Hit
| Entity | Dataset | Loan | Date | Lender | Status | Forgiveness |
|---|---|---|---|---|---|---|
| **MERCY HOUSE LIVING CENTERS, INC.** | ppp_150k_plus | $1,339,000 | 04/13/2020 | Banc of California | **Paid in Full** | **$1,348,905** (Jan 2021) |
| MERCY HOUSING AND SHELTER CORPORATION | ppp_150k_plus | $623,318 | — | Nutmeg State Financial CU | Exemption 4 | — |
| CAS ACQUISITION CO LLC | ppp_150k_plus | $262,500 | — | Bank Rhode Island | Paid in Full | — |

### Key Details — MERCY HOUSE LIVING CENTERS PPP:
- **Address:** 807 N GARFIELD ST, SANTA ANA, CA 92701-3821
- **Project County:** ORANGE
- **NAICS:** 624221 (Social Services, specifically homeless shelters)
- **All $1,339,000 = PAYROLL** — 100% payroll protection
- **259 jobs reported**
- **100% SBA Guaranty**
- **Forgiven Jan 2021** — full amount plus $9,905 accrued interest
- **HUBZone Indicator: Y** — Located in historically underutilized business zone

---

## 3. SIGNALS — HIGH PRIORITY

### 🚩 Signal 1: Related-Party Financing
- Mercy House Living Centers received $303,000 in FY2024 contributions from **Members of Board of Directors**
- This is direct related-party funding being routed through the CHDO entity structure

### 🚩 Signal 2: Deferred Money — Vagabond Inn Deal
- $13.5M seller carryback note from Casa Aliento LP to Mercy House CHDO
- Principal AND interest **DEFERRED** for 55 years
- ~$443K accrued interest as of June 2024
- **This defers repayment obligation indefinitely**

### 🚩 Signal 3: County Grant Used to Pay Private Lender
- CM Mercy House CHDO had a $7.9M loan from **Century Housing Corporation** (private CDFI lender)
- **$6.5M was paid down in Feb 2024 using County of Orange grant funds**
- This uses public money to pay a private lender = **debt extraction pattern**

### 🚩 Signal 4: Undrawn Public Loan
- 2nd and B Mercy House CHDO has $4.4M note from City of Oxnard Housing Dept
- Only **$439,921 drawn (10%)** as of June 2024
- **$3.96M in undrawn public commitment** sitting unused

### 🚩 Signal 5: Zero-Rent Public Lease
- Mercy House Living Centers pays **$0 rent** on Kraemer Place Shelter (County of Orange)
- In-kind benefit recorded at **$109K/year** — free public subsidy

### 🚩 Signal 6: PACEP Connection
- Mercy House Living Centers' NPPES taxonomy: **251B00000X** (Residential Treatment Facility)
- This entity type may be registered in PACEP as a licensed care facility
- **Cross-reference recommended against PACEP data**

---

## 4. AUTO-JOIN SCHEMA

### Key Join Fields for PPP ↔ CHDO ↔ LLC Cross-Reference

| Table | Key Fields | Join Target |
|---|---|---|
| `ppp_150k_plus` | `BorrowerName`, `BorrowerCity=SANTA ANA`, `ProjectCountyName=ORANGE` | MERCY HOUSE entity |
| `ppp_up_to_150k` | `BorrowerName`, `BorrowerCity`, `ProjectCountyName` | Broader Mercy search |
| `hb_llcs` | `Owner1`, `Owner2`, `SiteAddress`, `LastSeller` | CHDO board members |
| `hb_church_osint.entities` | `name`, `address`, `city=ORANGE COUNTY` | PACEP/OSINT entities |
| `nppes_export.oc_lb_orgs` | `org_name`, `city=SANTA ANA`, taxonomy=251B | Licensed facilities |

### Named Entities for OSINT Pivot:
- **Banc of California** — Servicing lender on Mercy House PPP; headquartered LA; potential bank records
- **Century Housing Corporation** — CDFI lender; connected to both CHDO deals and prior PPP
- **Casa Aliento LP** — LP counterparty in Vagabond Inn deal; possible related-party structure
- **807 N Garfield St, Santa Ana** — Mercy House HQ address
- **Vagabond Inn, Oxnard** — Property address involved in $15M sale/carryback

---

## 5. NEXT INVESTIGATION STEPS

1. **PACEP Cross-Reference**: Search PACEP for MERCY HOUSE LIVING CENTERS at 807 N Garfield St, Santa Ana — license status, inspection history, compliance records
2. **Banc of California Records**: Filed any SARs (Suspicious Activity Reports) on Mercy House accounts? What other nonprofit clients does Banc serve?
3. **Century Housing Corporation**: Full CDFI filing history; all CHDO loans originated; board member overlap with Mercy House
4. **Vagabond Inn Sale Chain**: Title search on Vagabond Inn (Oxnard) — who owns Casa Aliento LP? Track the $13.5M carryback to its source
5. **County of Orange Payments**: What other grants/leases exist between OC and Mercy House entities? Full payment history on file
6. **PPP → CHDO Timeline**: Map the April 2020 PPP forgiveness ($1.34M) against CHDO capital activity in 2020-2024
