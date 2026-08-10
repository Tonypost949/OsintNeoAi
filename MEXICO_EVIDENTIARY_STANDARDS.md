# EVIDENTIARY AUDIT STANDARDS: Mexico Cross-Border Conduit
**Document Status:** ACTIVE AUDIT WORKBOOK
**Target Authority:** Federal Prosecutorial & Joint Terrorism Task Force (JTTF) Review Standards

This document establishes the exact evidentiary baseline required to convert our active OSINT intelligence into admissible, court-ready evidence for the four international laundering nodes.

---

## 1. Culiacán SWIFT Node ($12.8M Interbank Clearing Conduit)
### Evidentiary Requirements & Current OSINT Mapping

*   **Requirement 1: Source of Funds** (Prove origin from diverted municipal/federal sources)
    *   *OSINT Status:* Correlated via Mercy House / RBA Builders board self-dealing logs in `forensic_master_spreadsheet.csv`.
    *   *Subpoena Target:* Direct municipal escrow and HUD disbursement account ledgers.
*   **Requirement 2: Intermediary Routing** (Prove movement through foreign bank accounts)
    *   *OSINT Status:* Identified international transaction patterns mapped in `MEXICO_FORENSIC_ANNEX.md`.
    *   *Subpoena Target:* correspondent bank SWIFT logs (MT103, MT202, ISO 20022 messages).
*   **Requirement 3: U.S. Real Estate Integration** (Prove funds acquired domestic properties)
    *   *OSINT Status:* Mapped to Falk Property Vector (`falk_1133_formosa.txt`, APN `5531007056` valued at $1.35M).
    *   *Subpoena Target:* Escrow instructions and ALTA Settlement Statements from the closing title company.

---

## 2. Tijuana Identity Conduit ($4.2M Identity Harvesting Operation)
### Evidentiary Requirements & Current OSINT Mapping

*   **Requirement 1: Fabricated/Stolen Identities**
    *   *OSINT Status:* Mapped 400+ compromised credentials in `HBPD_PORT_SCAN_REPORT.md` (Dehashed source logs).
    *   *Subpoena Target:* Certified state/federal identification databases compared with corporate formation filings.
*   **Requirement 2: Shell Entity Creation**
    *   *OSINT Status:* Mapped shell address networks (6,086 address nodes in `nodes.json`).
    *   *Subpoena Target:* Articles of Incorporation and Beneficial Ownership Information (BOI) filings from the FinCEN registry.
*   **Requirement 3: Concealed Beneficial Ownership**
    *   *OSINT Status:* Mapped direct links between corporate officers and Mercy House developers in `EVIDENCE_INDEX.md`.
    *   *Subpoena Target:* KYC/AML compliance folders from registered agents.

---

## 3. Juárez Transit Corridor ($3.1M Property Seizure Network)
### Evidentiary Requirements & Current OSINT Mapping

*   **Requirement 1: Coercion & Exploitation**
    *   *OSINT Status:* Mapped 4-year cycle of targeted eviction spikes co-located with immigrant demographics.
    *   *Subpoena Target:* Direct deposition/affidavits from displaced residents and recorded tenant communications.
*   **Requirement 2: Forced Property Transfers**
    *   *OSINT Status:* Property transaction shuffles ($2.8M) documented in `EVIDENCE_INDEX.md` (Section 4).
    *   *Subpoena Target:* County Recorder deeds showing sudden title changes post-eviction.
*   **Requirement 3: Financial Beneficiaries**
    *   *OSINT Status:* Mapped to board vendors (Pavalko, Bergman, Buntich) in the active audit workbook.
    *   *Subpoena Target:* Profit-and-loss statements of the managing real estate LLCs.

---

## 4. CDMX Registry Exploit ($18.5M Registry Manipulation)
### Evidentiary Requirements & Current OSINT Mapping

*   **Requirement 1: Database Alteration**
    *   *OSINT Status:* Documented asset `MX-CDMX-RPP-0012` valuation anomaly.
    *   *Subpoena Target:* Certified registry extracts and audit logs from the CDMX Public Registry of Property.
*   **Requirement 2: Intentional/Malicious Manipulation**
    *   *OSINT Status:* Correlated with U.S. municipal API gateway exposures (`api.huntingtonbeachca.gov` / `192.5.222.163`).
    *   *Subpoena Target:* Database administrator access tickets and system transaction logs.
*   **Requirement 3: Facilitation of Concealment**
    *   *OSINT Status:* Cross-referenced in `EVIDENCE_PACKAGE_WINDOWS.md`.
    *   *Subpoena Target:* Notarized deeds and international MLAT (Mutual Legal Assistance Treaty) records.

---
**END STANDARDS DIRECTIVE**
