# 🏛️ Dual-Chamber Lockbox System Architecture
**System:** OSINTNeoAI / Antigravity Cognitive Matrix  
**Architect:** Anthony Michael DeMarcello III (Makaveli Directive)  
**Classification:** Fiduciary Investigation & Autonomous Authority Routing Engine  
**Storage Tier:** `/storage/2004-1014/osintneoai_offload/evidence_locker/`

---

## 1. Core Operating Philosophy: The Dual-Chamber Lockbox

The platform is engineered around strict compartmentalization between **Citizen/User Experience** and **Backend Autonomous Reconnaissance**:

```
[Citizen / Whistleblower Intake]
               │
               ▼
   [CHAMBER 1: FRONTEND AIR-GAP]
   ├── Plain-English Risk Assessments (Grade A - F)
   ├── Scoped Contextual Wikipedia / Entity Mapping
   └── Zero PII / Zero Exploits / Zero Weaponized Code Exposure
               │
   ════════════╪════════════════════════════════════════════════ (Immutable Boundary)
               │
   [CHAMBER 2: THE BACKEND LOCKBOX]
   ├── Autonomous Security Telemetry (Katana, Nmap, WAF Auditors)
   ├── Multigo / Maltego XML & Graph Generation (Link Analysis)
   ├── Tokenized Hash Ledger (Anonymous Tracking ID)
   └── Automated Authority & Regulatory Dispatch (FOIA / CPRA / FinCEN / AG)
```

---

## 2. Chamber 1: Frontend User Experience (Zero Liability)

1. **Narrative Ingestion:**
   A citizen, resident, or whistleblower submits raw narrative testimony without requiring technical knowledge.
2. **Scoped Wikipedia Entity Contextualization:**
   * **Unindexed Entities:** Brand-new entities mentioned for the first time are minted as local candidate nodes following the user's initial structural taxonomy.
   * **Indexed Entities:** When an entity matches a known Wikipedia page (e.g., City of Huntington Beach, Orange County, or a state authority), the platform strictly surfaces *only* the specific facets, departments, and timelines brought up in the user's story—preventing irrelevant encyclopedic bloat.
3. **Plain-English Security & Exposure Reporting:**
   Users never see terminal commands, port scanning banners, raw packet dumps, or attack scripts. They receive plain-English risk assessments:
   * *Example:* "This municipal portal is properly protected behind enterprise shielding." vs. "This municipal portal leaves its administrative databases directly open to the open internet."

---

## 3. Chamber 2: Backend Autonomous Lockbox & Authority Routing

1. **Deep Network Reconnaissance & Audit:**
   The backend autonomously maps edge boundaries, checks for unshielded origin servers, identifies open administrative ports (RDP, MySQL, FTP), and scans for unauthenticated configuration leaks using Katana and socket verification.
2. **PII Quarantining & Compliance Gate:**
   Any detected Personally Identifiable Information (SSNs, private banking records, home addresses of non-public figures) is instantly stripped and placed into cold offline vault storage (`OFFLINE_EVIDENCE_VAULT`). It is never served to front-end users.
3. **Automated Regulatory & Authority Referral:**
   When critical vulnerabilities, systemic fraud, or municipal compliance violations are validated, the backend formats formal public records requests or official whistleblower disclosures:
   * **California CPRA / State FOIA:** Automated generation of formal public records requests to City Clerks and County Boards.
   * **Regulatory & Judicial Referrals:** Civil False Claims Act (CFCA), FinCEN SAR referrals, and municipal oversight submissions.
4. **Tokenized Anonymous Ledger:**
   Every investigation is assigned a cryptographic token (e.g., `INVESTIGATION-TOKEN-7F89B`). The user retains proof of submission and tracking status without their identity being tied to the public records requests.

---

## 4. Multigo / Maltego Graph Integration

Entities extracted from the intake story and enriched against authoritative registries are compiled directly into standard Maltego link-analysis specifications:
* **Schema:** `Source` | `Source.Type` | `Link.Label` | `Target` | `Target.Type`
* **Node Types:** `maltego.Person`, `maltego.Organization`, `maltego.Location`, `maltego.Document`, `maltego.Infrastructure`
* **Output Artifacts:**
  * Maltego CSV Import Wizard Matrix: `/storage/2004-1014/osintneoai_offload/evidence_locker/maltego_MUNICIPAL-CASE-001.csv`
  * Maltego XML Graph File: `/storage/2004-1014/osintneoai_offload/evidence_locker/maltego_MUNICIPAL-CASE-001.mtgl`

---

## 5. Fiduciary Compliance & Defensive Security Mandate

* **Evasive & Penetration Testing Handling:** All technical boundary diagnostics run strictly inside the backend lockbox. Telemetry is safely digested into defensive risk matrices and executive summaries.
* **No Weaponization:** The platform does not produce offensive execution scripts or copy-paste attack payloads. It diagnoses exposures, verifies boundaries, and ensures public sector accountability through verified public records and lawful disclosures.
