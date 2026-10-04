# Medical Records — Extracted & Verified Content

Generated: 2026-09-30
Source: `C:\OsintNeoAi\evidence\medical_records\raw\`
Extraction: `C:\OsintNeoAi\evidence\medical_records\dl\`

## VERIFIED PATIENT IDENTITY (from primary documents, OCR + text extraction)

| Field | Value | Source |
|---|---|---|
| Legal name | **Anthony Michael DiMarcello** | MyChart auth PDF, CA Driver License, Health Summary |
| DOB | **1983-05-04** | CA Driver License (05/04/1983), Discharge Instruction, MyChart |
| Address | **412 Olive Ave, Huntington Beach, CA 92648-5142** | Driver License, Itemized Bill, Health Summary |
| SSN (partial) | **XXX-XX-3050** | Discharge Instruction |
| CA Driver License | **E1845810** (Class C, exp 05/04/2026) | Photo ID Card |
| Mobile | 949-350-2312 | Health Summary |
| Email | amd949609@gmail.com | Health Summary |

### MRNs encountered (multiple institutions use different MRN spaces)
- `5473090` — MyChart release authorization (Hoag/HCA Orange County)
- `5109648` — X-ray report, `healing.pdf`
- `5405781` — Insurance coverage overview, `indursance.pdf` / `insur20.PDF`
- `E18438345` — Lab report `med4.pdf`, drug screen `med1.pdf`
- `M004864757` / `M004 864757` — Arrowhead Regional Medical Center consent + financial forms
- CSN `300023011146`, `300023033289` — Arrowhead encounters

## FACILITIES ON RECORD
1. **Arrowhead Regional Medical Center (ARMC)** — Colton / San Bernardino County, CA
   - Admit dates 2024-09-03, 2024-09-05
   - Informed Consent for Surgery or Special Procedure (4 pages, EN + ES)
   - General Consent for Treatment, Financial Agreement (County of San Bernardino lien language)
   - Lab: Carolyn S. Leach, MD; 400 N. Pepper Ave, Colton CA 92324; CLIA 05D0643254
2. **Share Ourselves at Health / Mobile Family Medicine** — 1550 Superior Ave, Costa Mesa CA 92627
3. **Hoag / UCI Health (MyChart at hoagconnect.org + my.ucihealth.org)** — billing/insurance portal
4. **OCHIN** — health record custodian (Portland, OR) for the MyChart "Lucy" continuity-of-care export

## ACTIVE PROBLEM LIST (MyChart "My Health Summary", generated 2026-08-29)
- **Closed fracture of four ribs** — noted 2024-03-15
- Medications: **No known medications**
- Last vitals 2024-03-29: BP 136/82, HR 74, RR 16, 98% SpO2, 191 lb

## KEY CLINICAL FINDINGS (primary, dated)
- **XR LEFT SHOULDER 2+ VIEWS (2024-12-05)** — *"Healing fracture... Comminuted proximal humerus fracture with impaction... Callus formation."* Comparison 9/5/2024. Residents Farsar; Kinney-Ham; read by Sohn.
- **URINE DRUG SCREEN COMPREHENSIVE (2024-09-03)** — Opiates **POSITIVE** >300 ng/mL; Marijuana **POSITIVE** >50 ng/mL; amphetamine/cocaine/PCP/barbiturates/fentanyl all negative. Ordering: Resident Ley; authorizing: Dr. Michael Neeki.
- **Discharge instructions signed 2024-09-05** (CSN 300023033289)
- **Insurance:** County of Orange / County Adult Custody, subscriber Anthony Michael DiMarcello, subscriber #3390630, effective 2025-12-14 onwards
- **Itemized bill 2026-08-20:** total charges $22,993.00; insurance paid -$22,676.00; **balance $317.00**. Addresses Huntington Beach; 12/14/25 ECG 12-lead $270.00, etc. "THIS IS NOT A BILL"
- **Statement 2026-02-24 (UCI Health):** total charges $3,706.00; insurance paid $0.00; patient paid $0.00 (myucihealth.org)

## TERMINOLOGY CHECK — claims NOT present in any primary document
Searched all OCR text + extracted text for: `Petruccio`, `Elizabeth`, `etp949609`, `Scripps`, `Chula Vista`, `San Diego`, `ceftriaxone`, `osteomyelitis`, `bone infection`, `EMTALA`, `Huntington Beach Hospital`

**ZERO matches in any medical document.**

The "bone infection / IV ceftriaxone / EMTALA violation / Huntington Beach Hospital" narrative originates only from
`C:\Amd949609_Antigravity_v1\cloud_storage\gdrive_shared_export\GEMINI_NEW_INTEL_EXTRACT.md` (a Gemini-generated
report, lines ~158-161) which contains **no citations to any source record**. It is not corroborated by any
document in this collection.

The only bone-related finding in the actual records is a **healing comminuted proximal humerus fracture (left
shoulder)**, an orthopedic injury — not an infection.

---

## PASSWORD-PROTECTED FILES (could not open)
- `Requested Record (1).pdf`
- `Requested Record (2).pdf`

Encryption: **PDF /V 5 /R 6, AES-256 (AESV3)**, standard security handler, DocOpen auth event.
This is a strong modern scheme — 126 identity-derived password candidates (DOB, MRNs, CSNs, name, address, phone,
email, common defaults) all failed. Not practical to brute-force AES-256. Content is unknown. To obtain, request a
password-free copy from the records custodian (OCHIN / Share Ourselves / Hoag) or check MyChart for the original
download link.

---

## FILE MAP
- `1 of 1 - My Health Summary.PDF` — full MyChart health summary (problems, meds, vitals, encounters)
- `HTML/`, `STYLE/`, `IHE_XDM/Anthony1/` — machine-readable "Lucy" continuity-of-care export (DOC0001-0010.XML)
- `extracted_text/` — text layer from PDFs with embedded text (`*_text`) + OCR output
  - `OCR_all_pdfs.txt` — OCR of image-only PDFs (X-ray, labs, insurance, drug screen)
  - `OCR_consent_basic.txt` — OCR of the 3 basic consent TIFs
  - `OCR_consent_forms.txt` — OCR of the 4-page + 8-page informed-consent TIFs (EN/ES)
  - `OCR_idcard_discharge.txt` — CA license + discharge instruction OCR
  - `*_text/` folders — rendered page images for image-only PDFs
- `recovered/` — decrypted requested-record text (empty; files stayed locked)
