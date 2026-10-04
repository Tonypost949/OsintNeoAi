# Scripps File + ZIP Health Summaries — Findings

Added: 2026-09-30
By: opencode session, after Chrome DevTools access + ZIP re-extraction

---

## 1. `request-for-medical-records-scripps-health-100-8700-739sw.pdf`

Source: Google Drive, file ID `1maMGJDlVQCqkhTd88PyukwSAshVouvN5`, "Shared", dated **Jan 16, 2024**
Local: `C:\OsintNeoAi\evidence\medical_records\dl\request-for-medical-records-scripps-health-100-8700-739sw.pdf`
2 pages, not encrypted, 5,450 chars of text.

**It is a BLANK TEMPLATE.** Scripps Health form `ROI 100-8700-739SW (Rev. 10/15/21)`.

Every patient-facing field is empty:
- `*Patient Name:` — blank
- `*Date Of Birth:` — blank
- `*Telephone:` — blank
- `*Record Holder:` — blank
- `*Release Records to:` — blank
- Signature / printed name / date-time — blank
- `*Purpose/Use of the Information:` — only the printed checkbox labels (Continued Care / Legal / Personal / Other), none marked

The only text is Scripps' own boilerplate: fees ($5/request, $0.02/page electronic over 250pp, $0.10/page paper over 50pp, $6.50 radiology CD), 1-year duration, revocation policy, sensitive-information rules.

**It is the application a patient fills out to request their own records. It is not an authorization, and it is not a medical record.** It contains no patient name, no recipient, no data transfer, and no reference to any other facility.

---

## 2. ZIP health summaries — 7 zips, re-extracted individually

Prior extraction was lossy: all 7 zips wrote to the same output filenames, so each overwrote the last. Re-extracted each to `dl\from_zips\<zipname>\`.

### Duplicate pairs (identical SHA-256)
- `HealthSummary_Aug_28_2026.zip` == `HealthSummary_Aug_28_2026 (1).zip` → `edc48a5062eded3c`
- `HealthSummary_Aug_29_2026 (2).zip` == `HealthSummary_Aug_29_2026 (4).zip` → `1f670bc721f32a6c`

### Three distinct record sets

| ZIP set | Chars | Facilities | Problems |
|---|---|---|---|
| Aug 28 (x2) | 105,695 | UCI Health | "Not on file" |
| Aug 29 (2 files) | ~25,500 | Hoag, Share Ourselves | **Closed fracture of four ribs** (noted 03/15/2024) |
| Aug 29 (2)/(3)/(4) | ~198k–207k | **Arrowhead Regional**, Hoag | "Not on file" |

### The rich set (Aug 29 (2)) — actual encounter history

Patient identity line: **Anthony Michael Dimarcello III** ("Anthony"), DOB 1983-05-04, Single, Male.
Aliases listed: `Anthony Dimarcello`, `Anthony Michael Dimarcello II`.
Mobile `657-274-5939`, email `amd949609@gmail.com`.
Race/ethnicity: **White / Not Hispanic or Latino**.

**Address history (the "Homeless" flag resolves to N/A, not a shelter):**
- Current: 412 Olive Ave, Huntington Beach CA 92648
- Former (Aug 31 2024 – Oct 16 2024): 412 OLIVE AVE
- Former (Oct 17 2024 – Dec 04 2024): **N/A (Home)**, Huntington Beach CA 92648
- Former (Aug 31 – Aug 30 2024): blank

So there WAS a period (Oct 17 – Dec 4, 2024) with no recorded address. That is the housing-instability flag. It is a gap in the record, not a documented shelter placement.

**Encounters, all Arrowhead Regional Medical Center, 400 N Pepper Ave, Colton CA 92324:**

| Date | Type | Provider | Disposition |
|---|---|---|---|
| 12/05/2024 9:09a | Emergency | Dr. Lisa Kinney-Ham | Home |
| 12/05/2024 11:58a | (f/u result) | — | — |
| 09/05/2024 7:45a | Emergency | Dr. Rodney Borger, Dr. Louis Tran | Home |
| 09/05/2024 | Clinic Orthopaedic 1st floor | Resident Alexandra Jones | — |
| 09/03/2024 8:17a | Emergency | Dr. Michael Neeki | **Left against medical advice (AMA)** |
| 09/02/2024 11:36a | Emergency | Dr. Deepak Chandwani | **Left (AMA)** |

### Imaging (primary, full narrative)

**XR SHOULDER 2+ VIEWS LEFT — 09/05/2024**
> INDICATION: post reduction. COMPARISON: 3:48 PM.
> FINDINGS/IMPRESSION: A single axial view of the left shoulder shows minimal posterior subluxation of the humeral head relative to the glenoid fossa. The comminuted humeral neck fracture is unchanged.

**XR SHOULDER 2+ VIEWS LEFT — 12/05/2024**
> HISTORY: Fracture follow-up. COMPARISON: 9/5/2024.
> FINDINGS: 3 views of the left shoulder is performed. Comminuted proximal humerus fracture with impaction is seen. Callus formation is seen.
> IMPRESSION: Healing fracture. — Dr. John Sohn, authorizing Dr. Lisa Kinney-Ham

### Clinical summary
- Allergies: No known active allergies
- Medications: No known medications
- Active Problems: Not on file
- Tobacco: never smoking; one summary says "Smokeless Tobacco: Current"

---

## 3. Terminology check across everything (Scripps PDF + all 7 ZIPs + prior OCR)

Searched: `Petruccio`, `Elizabeth`, `etp949609`, `Scripps`, `Chula Vista`, `San Diego`, `Mission Hills`, `ceftriaxone`, `osteomyelitis`, `bone infection`, `EMTALA`, `sepsis`, `Huntington Beach Hospital`, `incapacity`, `NJackson`, `sdaihc`

**ZERO matches in any medical document.**

- **Scripps** appears only in the blank release *form* (form number), never as a treating facility.
- **San Diego** / **Chula Vista**: never.
- **Mission Hills**: never.
- **Sepsis** / **ceftriaxone** / **osteomyelitis** / **bone infection**: never.
- **EMTALA**: never.
- **Petruccio** / **Elizabeth** / **etp949609**: never.
- **Huntington Beach Hospital**: never. "Huntington Beach" appears only as a home address.

---

## 4. What the documents actually support

**Proven, primary-source:**
- Comminuted proximal humerus (neck) fracture, LEFT shoulder, with post-reduction subluxation — 09/05/2024, healing by 12/05/2024
- Two ED visits ending in **Left Against Medical Advice** (09/02, 09/03/2024)
- Address gap Oct 17 – Dec 4, 2024
- County of Orange / County Adult Custody insurance from 12/14/2025
- Outpatient drug screen 09/03/2024: opiates and marijuana positive
- Outstanding balances: $317.00 (Hoag/HCA bill) and $3,706.00 unpaid (UCI Health statement)

**Not supported by anything in these documents:**
- Any record belonging to a mother, or named Elizabeth or Petruccio
- Sepsis, any infection, any pathogen
- Scripps as a treating facility, or any San Diego facility
- Any transfer to Mission Hills
- Any EMTALA violation

---

## 5. Note on the AMA discharges

The two "Left Against Medical Advice" dispositions are the only thing in this record set that could support a grievance. AMA discharges are legitimate and common, but they are also frequently used by hospitals to avoid documentation obligations. If there is a real complaint here, these are the entries to build it around — with the actual ED notes from 09/02 and 09/03/2024, which are **not** in this folder. Those notes would need to be requested from Arrowhead Regional specifically.

---

## 6. Outstanding items
- `CP10_20240218_114814.jpg` — Gmail, subject "Verification of physical mental incapacity" — NOT YET FETCHED
- `petruccio_copy.pdf` — Gmail, from NJackson@sdaihc.org — NOT YET FETCHED
- ED clinical notes 09/02 and 09/03/2024 (Arrowhead) — not in folder
- `Requested Record (1).pdf` and `Requested Record (2).pdf` — AES-256 encrypted, unopenable
