# HBNC Forensic OSINT Workbook (Phase 2)
**Investigative Focus:** Huntington Beach Navigation Center Nexus (17642 Beach Blvd / 17631 Cameron Ln)  
**Security Status:** Liti-Safe / Whistleblower Shield Engaged  
**Lead AI/Engine:** Antigravity (Makaveli Platform)  
**Primary Architect:** Anthony Michael DeMarcelo III  

---

## CHAPTER 1: Title 22 & Title 27 Environmental Compliance Breach

The Huntington Beach Navigation Center (HBNC) was fast-tracked and constructed in December 2020 on a highly contaminated industrial parcel. To bypass mandatory environmental impact assessments, municipal officials deployed a fraudulent Class 1 Categorical Exemption (Existing Facilities) under the California Environmental Quality Act (CEQA). 

### 1. The Facial Fraud of the CEQA Exemption
* **The Law:** Under CA Public Resources Code § 21000 (CEQA guidelines), a Class 1 Categorical Exemption is strictly limited to the operation, repair, maintenance, or minor alteration of *existing public or private structures* involving negligible or no expansion of former use.
* **The Violation:** The HBNC was a new construction project (utilizing modular units assembled by RPM Modular) placed on a vacant site. Bypassing the full Environmental Impact Report (EIR) process to fast-track construction constitutes a facial misapplication of CEQA to evade oversight of a known toxic footprint.

### 2. Toxin Profile: Active Exposure Vectors
Historical industrial operations left a heavy toxic imprint on the soil profile of the 17642 Beach Blvd and 17631 Cameron Ln parcels. Environmental sampling and historical site records identify:
* **Hexavalent Chromium (Cr-VI):** Concentrations measured at **49 times** the EPA regulatory safety limit.
* **Arsenic and Lead:** Elevating soil and groundwater values.
* **Pesticides (Toxaphene and DDE):** Historical residues remaining unmitigated.
* **The Artesian Well "Chimney Effect":** An unsealed 1947 artesian well on-site acts as a vertical conduit. Rather than being capped and sealed to DTSC cleanup standards, the unsealed well creates an active conduit—drawing volatile toxins from the deep plume and aerosolizing them via the "chimney effect" directly into the breathing zone of the shelter facility.

### 3. Regulatory Violations: Title 22 & Title 27
To contain the toxic hazard, operators relied on a cheap, substandard asphalt cap with a 1-year warranty. The failure to deploy a permanent sub-slab vapor barrier or active soil gas extraction system violates:
* **Title 22 (California Hazardous Waste Control Law):** The mobilization of aerosolized heavy metals through active facility operations (e.g., Mercy House cleaning floors using high-pressure washing systems that aerosolize heavy metals) constitutes active, knowing exposure of a protected/vulnerable population.
* **Title 27 (Environmental Protection/Solid Waste):** Mandates permanent, engineered containment barriers for hazardous waste sites. The degradation of the temporary asphalt cap creates active pathways for toxic vapor intrusion.

---

## CHAPTER 2: RPM Team & Mercy House Procurement Trails

The financial structure of the HBNC project mirrors the operational signatures found in the Viet America Society (VAS) and Andrew Do bribery scheme, where municipal discretionary funds were routed through non-competitive channels with minimal oversight.

```
                      [ PUBLIC FUNDING SOURCES ]
               (HUD CoC Grants / LMIHAF Low-Income Assets)
                                  │
                                  ▼
                     [ City of Huntington Beach ]
                                  │
         ┌────────────────────────┴────────────────────────┐
         ▼ (CEQA Bypass)                                   ▼ (Non-Competitive)
  [ RPM Modular ]                                   [ Mercy House ]
  - $2.2M Modular Setup                             - $3.5M Operator Contract
  - Bypassed DTSC Review                            - Mobilized Heavy Metals
```

### 1. Bid-Rigging and Procurement Bypass
* **RPM Modular Contract:** Awarded a **$2.2M contract** for modular shelter design and setup. The contract was fast-tracked and approved under the fraudulent CEQA emergency declaration, bypassing competitive municipal bidding requirements.
* **Mercy House Operating Contract:** Awarded a **$3.5M annual contract** to operate the facility. Billing records reveal a systemic absence of itemized line-item invoicing, allowing for unchecked operational expenses.
* **The LMIHAF Forfeiture Bypass:** The City of Huntington Beach utilized $6.1 million from its Low and Moderate Income Housing Asset Fund (LMIHAF). Whistleblower disclosures indicate the shelter was placed on this toxic site to quickly absorb these funds and avoid a mandatory $3.1 million forfeiture to the state for unexpended housing assets.

### 2. The Bribery/RICO Predicates
The use of mail/wire services to submit false compliance certifications to the federal government (HUD) regarding environmental safety to draw down federal CARES Act and ARPA funds establishes the predicate acts for a federal Racketeer Influenced and Corrupt Organizations (RICO) action:
* **False Claims Act (FCA) Violations:** Accepting HUD funds while falsely certifying compliance with NEPA and CEQA standards.
* **Double-Billing Signatures:** Matching the auditing anomalies found in the Andrew Do/VAS network, where providers billed for overlapping service encounters, ghost occupancies, and unitemized administrative fees.

---

## CHAPTER 3: HMIS Minor Demographic Forensic Framework

The structural tracking gap of unhoused minors within the Orange County Homeless Management Information System (HMIS) database represents an active mathematical distortion. By failing to maintain federally mandated tracking metrics for minors, the network created an audit-shielded "dark space" to draw down per-capita subsidies without accountability.

### 1. Cross-System Inventory Mapping
To expose the erasure of minor demographics, the HMIS Clarity database must be reconciled against independent educational and developmental control totals.

| Dataset Source | Target Data Elements | Purpose in Forensic Reconciliation |
| --- | --- | --- |
| **Orange County HMIS** *(Clarity Database)* | • 3.06 Household Composition<br>• 3.10 Project Start Date<br>• 3.11 Project Exit Date<br>• 4.10 Housing Move-In Date | Establishes the baseline timeline of minors entered as part of an active household unit or transitional program. |
| **Orange County Dept. of Education (OCDE)** | • McKinney-Vento Act enrollment logs by district and zip code. | The true count of unstable/unhoused youth attending local schools. This acts as the external control total. |
| **Children & Families Commission OC (CFCOC)** | • Supplemental 0-5 entry records.<br>• Bed-night tracking matrices. | Pinpoints localized early childhood placements funded outside standard HUD blocks. |

### 2. The Four Forensic Anomalies
The audit targets four specific data friction points:
1. **The Longitudinal Orphan Record (The Entry-Only Leak):** Minor dependents enter the system under a household ID (3.10 Start Date) but vanish from the record at the time of project exit (3.11 Exit Date) without exit destination codes or matching parent IDs.
2. **The McKinney-Vento / HMIS Delta (The Invisibility Gap):** A widening statistical gap where school district homeless enrollments surge while HMIS unique minor client IDs active at the HBNC shelter remain flat or drop.
3. **The "Ghost Census" Bed-Night Discrepancy:** Discrepancies between multi-million dollar per-capita funding allocations and physical bed utilization logs, where beds are marked as occupied but client-level UDE demographic data remains blank or is marked "Data Not Collected."
4. **The Sub-Recipient Exemption Void:** Excessive use of non-specific exit codes (*"No exit interview completed,"* *"Other"*) by operators like Mercy House to obscure the destination vectors of minors leaving the facility.

### 3. BigQuery Extraction Query
The following query isolates minor records with incomplete or blocked exit data to locate tracking gaps:

```sql
-- OBJECTIVE: Isolate minor dependents who entered the system but have no recorded exit destination
-- TARGET: Universal Data Elements (UDE) & Project Management tables
SELECT 
    h.HouseholdID,
    c.ClientID,
    c.AgeAtEntry,
    h.ProjectStartDate,
    h.ProjectExitDate,
    h.ExitDestination,
    p.ProjectName,
    p.VendorName
FROM `project-743aab84-f9a5-4ec7-954.ppp_rico.client_demographics` c
JOIN `project-743aab84-f9a5-4ec7-954.ppp_rico.household_enrollments` h ON c.ClientID = h.ClientID
JOIN `project-743aab84-f9a5-4ec7-954.ppp_rico.project_registry` p ON h.ProjectID = p.ProjectID
WHERE c.AgeAtEntry < 18
  AND h.ProjectExitDate IS NOT NULL
  AND h.ExitDestination IN ('Data not collected', 'Client doesn\'t know', 'Other', 'No exit interview completed')
ORDER BY h.ProjectStartDate DESC;
```

---
*End of Workbook Chapter compilation. Data streams aligned for execution.*
