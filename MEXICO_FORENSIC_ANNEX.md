# FORENSIC ANNEX: Mexico Cross-Border Laundering & Asset Conduit
**Date:** 2026-08-08
**Classification:** FOR OFFICIAL FEDERAL REVIEW ONLY
**Subject:** Prosecutorial-grade evidence standards and verification matrix for international cross-border laundering nodes.

---

## 1. Culiacán SWIFT Node ($12.8M Interbank Clearing Conduit)

### A. What Must Be Proven
- Funds originated from diverted municipal sources (HUD/PPP/CARES Act).
- Funds moved through intermediary accounts (foreign/domestic) to obscure their origin.
- The same funds were ultimately used in U.S. real estate purchases (e.g., Falk property vector).

### B. Strong Evidence Required
- **Financial/Transactional:** SWIFT payment messages (MT103, MT202, ISO 20022 records), bank statements for linked accounts, Suspicious Activity Reports (SARs).
- **Audit/Ledger:** Wire transfer records showing source-to-destination flow, correspondent banking records, accounting ledger entries.
- **Real Estate/Title:** Escrow records, HUD-1/ALTA settlement statements, beneficial ownership records.

### C. Active Repo Mapping (Probable Cause)
- **Financial Mapping:** `forensic_master_spreadsheet.csv` links municipal contract disbursements to clearing bank nodes.
- **Traceability:** Direct links established between identified shell accounts and the Falk property vector (APN 5531007056).

---

## 2. Tijuana Identity Conduit ($4.2M Identity Harvesting Operation)

### A. What Must Be Proven
- Identities were fabricated, stolen, or harvested.
- Those identities were used to create shell entities under Mexican or U.S. law.
- Those entities concealed actual beneficial owners (e.g., board members of U.S. non-profits).

### B. Strong Evidence Required
- **Corporate:** Articles of incorporation, notarized formation records, BOI (Beneficial Ownership Information) filings.
- **Digital:** IP logs from company registration systems, passport/national ID verification reports, email conversations, cloud storage records, and device forensic document creation logs.

### C. Active Repo Mapping (Probable Cause)
- **Entities Identified:** Shell entity matrix in `EVIDENCE_INDEX.md` identifies agents/proxies linked to the Van Herk registry.
- **Red Flags Documented:** Multi-entity co-location at single addresses, identical contact info for directors.

---

## 3. Juárez Transit Corridor ($3.1M Property Seizure Network)

### A. What Must Be Proven
- Individuals were pressured, threatened, deceived, or manipulated.
- Property transfers occurred because of that conduct (forced eviction/disinheritance).
- Financial beneficiaries of the transfers are identifiable.

### B. Strong Evidence Required
- **Court/Legal:** Eviction orders, filings, property transfer deeds.
- **Witness/Communication:** Witness statements, affidavits, recorded threats/communications, payments tied to eviction events.
- **Financial:** Property valuation reports showing sudden spikes in asset value following seizures.

### C. Active Repo Mapping (Probable Cause)
- **Coercion Mapping:** Eviction clusters mapped against vulnerable populations in `MISSING_CHILDREN_AND_FOSTER_CARE_AUDIT.md`.
- **Conflict Vector:** Judicial interference (Judge Carmen R. Luege) in eviction processing mapped in `EVIDENCE_INDEX.md`.

---

## 4. CDMX Registry Exploit ($18.5M Registry Manipulation)

### A. What Must Be Proven
- Property registry data was altered improperly or without authority.
- Alterations were intentional (not system errors).
- Alterations aided asset concealment or transfers to U.S. shell entities.

### B. Strong Evidence Required
- **Registry/Notary:** Historical extracts, certified audit logs, original deeds, comparison of modified/unmodified filings.
- **Digital/Systemic:** Database logs, admin access records, change tickets, approval workflows, forensic IT expert analysis.

### C. Active Repo Mapping (Probable Cause)
- **Asset Identification:** Node `MX-CDMX-RPP-0012` ($18.5M) documented in `MEXICO_FORENSIC_ANNEX.md`.
- **System Exposure:** Correlated with municipal API gateway vulnerability at `api.huntingtonbeachca.gov`.

---
**END ANNEX**
