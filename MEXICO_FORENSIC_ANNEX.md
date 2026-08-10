# FORENSIC INVESTIGATION STANDARDS: Mexico Cross-Border Laundering & Asset Conduit
**Date:** 2026-08-08
**Classification:** FOR OFFICIAL FEDERAL REVIEW ONLY
**Subject:** Prosecutorial-grade evidence standards, tracing frameworks, and verification matrices for international cross-border laundering nodes.

---

## 1. Culiacán SWIFT Node ($12.8M Interbank Clearing Conduit)

### A. What Must Be Proven
*   **Source of Funds:** Proof that the $12.8M originated from diverted or fraudulently acquired U.S. municipal, HUD, PPP, or CARES Act sources.
*   **Layering/Concealment:** Proof that funds moved through complex intermediary accounts (foreign and domestic shell companies) to intentionally obscure their illicit origin.
*   **Integration:** Conclusive tracing showing that the exact laundered funds were ultimately used to execute U.S. real estate acquisitions (e.g., the Falk property vector, APN `5531007056`).

### B. Core Evidentiary Requirements & Tracing Standard
To sustain a federal indictment, investigators must construct a continuous, unbroken chain of transaction records following this flow:

```
[Municipal / Federal Grant Accounts]
                 ↓
      [Vendor / Shell Entity]
                 ↓
    [Foreign Bank Account (MX)]
                 ↓
  [Intermediary Clearing Account]
                 ↓
      [U.S. LLC / Trust Node]
                 ↓
   [Real Estate Asset Acquisition]
```

### C. Strong Admissible Evidence
*   **SWIFT Messages:** Raw SWIFT MT103 (Single Customer Direct Wire Transfer), MT202 (General Financial Institution Transfer), and ISO 20022 XML financial messages documenting transaction routing, sender/receiver bank identification codes (BICs), and clearing paths.
*   **Interbank Statements:** Complete bank statements for all linked correspondent and intermediary accounts involved in the transit chain.
*   **Suspicious Activity Reports (SARs):** FinCEN or foreign equivalent regulatory filings flagged against the clearing intermediaries.
*   **Transactional Records:** Wire transfer records showing explicit source-to-destination flow, including correspondent bank clearing logs.
*   **Escrow & Settlement Documentation:** Escrow instructions, HUD-1, and ALTA Settlement Statements for the final U.S. real estate acquisitions linking the purchasing LLC or Trust back to the intermediary clearing accounts.
*   **Beneficial Ownership:** Ultimate Beneficial Ownership (UBO) declarations and corporate resolutions linking the purchasing trusts directly to the source shell entities.

### D. Corroborating Evidence
*   **Internal Communications:** Emails, messaging logs, or ledger entries discussing the execution and timing of wire transfers.
*   **Insiders/Whistleblowers:** Insider ledger records or testimony from bank employees, compliance officers, or co-conspirators.

---

## 2. Tijuana Identity Conduit ($4.2M Identity Harvesting Operation)

### A. What Must Be Proven
*   **Identity Theft:** Stolen, fabricated, or deceased-person identities were harvested and used to register entities.
*   **Shell Registration:** The fraudulent identities were used to register and incorporate shell companies under Mexican or U.S. law.
*   **Concealment of Beneficial Owners:** These entities were created with the specific intent to hide the true beneficial owners and facilitate illicit capital placement.

### B. Red Flags to Audit
*   **Co-Location:** Multiple entities registered to the exact same physical or mailing address without operational business logic.
*   **Contact Overlap:** Repeated use of identical telephone numbers, email addresses, or notary proxies across supposedly unrelated entities.
*   **Nominee Directors:** Nominee directors or registered agents with no actual business involvement, frequently appearing across hundreds of unrelated corporate filings.

### C. Strong Admissible Evidence
*   **Articles of Incorporation:** Certified articles of incorporation, bylaws, and notarized company formation records from Mexico (S.A. de C.V.) and the U.S. (LLC).
*   **Identity Documentation:** Copies of counterfeit or stolen identifications, passports, or national ID numbers (CURP/RFC in Mexico) used during the corporate registration process.
*   **Beneficial Ownership Filings:** Corporate resolutions, nominee agreements, and FinCEN Beneficial Ownership Information (BOI) reports.
*   **Digital Forensic Records:** IP address logs, session data, and transaction times retrieved from online company registration systems.
*   **Credential Verification Reports:** Passport and national ID verification reports confirming the fraudulent status of the registered names.

### D. Corroborating Evidence
*   **Digital Evidence:** Forensic extraction of emails, encrypted chat histories, and cloud storage records discussing the acquisition and deployment of harvested identities.
*   **Device Forensics:** File metadata and system logs demonstrating the localized creation or modification of registration documents.

---

## 3. Juárez Transit Corridor ($3.1M Property Seizure Network)

### A. What Must Be Proven
*   **Coercion & Fraud:** Vulnerable individuals, mixed-status families, or tenants were pressured, threatened, deceived, or illegally manipulated.
*   **Forced Transfer:** The predatory behavior directly resulted in property transfers, unlawful evictions, or surrender of housing assets.
*   **Identifiable Beneficiaries:** Specific corporate entities, municipal actors, or landlords pocketed the financial benefits of these forced transfers.

### B. Core Evidentiary Requirements
Because coercion and civil rights deprivation involve high criminal standard thresholds, direct evidence is mandatory:

*   **Eviction Filings:** Raw court records, unlawful detainer filings, and sheriff/marshal execution logs.
*   **Title/Deed Records:** Property transfer deeds, quitclaim deeds, and sudden title changes executed immediately following coercive actions or predatory evictions.
*   **Communications Log:** Text messages, emails, voicemails, or recorded calls containing instructions, threats, or coordinated actions to evict or force out occupants.
*   **Witness Affidavits:** Direct witness statements and sworn affidavits from affected tenants, occupants, and neighbors documenting the pattern of harassment.
*   **Financial Flow:** Bank ledgers and transactional records showing payments to eviction enforcers, security firms, or municipal actors linked directly to eviction events.

### C. Particularly Persuasive Evidence
*   **Pattern of Exploitation:** Documentation showing a repeated, identical eviction pattern targeting uncounted families across multiple properties managed by the same entities (e.g., Mercy House / Shea Homes networks).
*   **Sudden Value Spikes:** Property valuation reports showing rapid asset re-evaluations immediately following the forced removal of rent-restricted or uncounted tenants.

---

## 4. CDMX Registry Exploit ($18.5M Registry Manipulation)

### A. What Must Be Proven
*   **Unauthorized Modification:** Official property registry databases or files were altered improperly or without legal authority.
*   **Intentionality:** The alterations were executed intentionally, not as a system error.
*   **Laundering Utility:** The registry manipulations directly facilitated asset concealment, fraudulent title transfers, or the hiding of illicit capital.

### B. Strong Admissible Evidence
*   **Historical Registry Extracts:** Certified historical extracts of the property registry (Folio Real in Mexico City) showing the complete chain of ownership and any abrupt alterations.
*   **Audit Logs:** System audit logs retrieved from the CDMX Property Registry (`Registro Público de la Propiedad y de Comercio`) showing the user accounts, IP addresses, and timestamps of the modifications.
*   **Access Records:** User access lists, authentication logs, and database transaction queries linking the alterations to specific system administrators or credentials.
*   **Original Deeds:** Original physical deeds and notary protocols (`escrituras públicas`) to compare against the modified digital registry entries.
*   **Notarial Records:** Official books and audit records kept by the executing Notary Public (`Notario Público`) confirming the lack of valid authorization for the registry changes.

### C. Digital Forensic & Corroborating Evidence
*   **Registry Database Logs:** SQL transaction logs, change tickets, and system approval workflows.
*   **Expert Analysis:** Digital forensic report from certified experts confirming unauthorized administrative modifications or system manipulation.
*   **Witness Testimony:** Sworn testimony or internal investigation findings from registry employees or system auditors.

---
**END STANDARDS**
