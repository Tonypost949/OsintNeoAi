# FORENSIC ANNEX: Mexico Cross-Border Laundering & Asset Conduit
**Date:** 2026-08-08
**Classification:** FOR OFFICIAL FEDERAL REVIEW ONLY
**Subject:** Prosecutorial-grade evidence standards and verification matrix for international cross-border laundering nodes.

---

## 1. Culiacán SWIFT Node ($12.8M Interbank Clearing Conduit)
### What must be proven
- Funds originated from diverted municipal sources.
- Funds moved through intermediary accounts to obscure their origin.
- The same funds were ultimately used in U.S. real estate purchases.
### Strong evidence
- SWIFT payment messages (MT103, MT202, ISO 20022 records).
- Bank statements for all linked accounts.
- Suspicious Activity Reports (SARs) where legally obtainable.
- Wire transfer records showing source-to-destination flow.
- Correspondent banking records.
- Escrow records from property purchases.
- Closing statements (HUD-1, ALTA Settlement Statements).
- Beneficial ownership records linking purchasers to source entities.
### Financial tracing standard
Investigators generally build:
```
Municipal Account
↓
Vendor / Shell Entity
↓
Foreign Bank Account
↓
Intermediary Clearing Account
↓
U.S. LLC / Trust
↓
Real Estate Acquisition
```
### Potential corroboration
- Emails discussing transfers.
- Accounting ledger entries.
- Internal approval records.
- Testimony from bank employees or insiders.

---

## 2. Tijuana Identity Conduit ($4.2M Identity Harvesting Operation)
### What must be proven
- Identities were fabricated or stolen.
- Those identities were used to create entities.
- Those entities concealed actual beneficial owners.
### Strong evidence
- Corporate formation records.
- Articles of incorporation.
- Beneficial ownership filings.
- Notarized incorporation documents.

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
