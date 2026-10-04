# Elizabeth Tina Petruccio — Mission Hills Face Sheet (Primary Source)

Source: `C:\OsintNeoAi\evidence\medical_records\raw\fwdfacesheet\fs.pdf`
- 2 pages, screen-capture printed to PDF (producer: PDF-XChange Standard, PDF 1.4)
- Created: **2026-03-13 14:11 PT** (header timestamp: "Mar 13, 2026 14:09:37 PT")
- No text layer, no form fields, no annotations -> content recovered by OCR only
- OCR performed with two independent engines (Windows.Media.Ocr, Tesseract 400-900 dpi, EasyOCR 300 dpi); results agree

## Page 1 — Resident information
| Field | Value |
|---|---|
| Facility | Mission Hills Post Acute Care, 3680 Reynard Way, San Diego, CA 92103-3847, TEL (619) 297-4484 |
| Resident name | PETRUCCIO, ELIZABETH TINA |
| Birthdate / Age | 07/29/1964 / 61 |
| Sex | F |
| SSN | 143-60-5120 |
| Medicare HIC | 93931022D |
| Medicare Beneficiary ID | 93931022D |
| Medicaid # | 93931022D (OCR ambiguous) |
| Admission Date | 02/17/2024 |
| Init. Adm. Date | 02/17/2024 |
| Orig. Adm. Date | 02/17/2024 |
| Previous address | HOMELESS, SAN DIEGO, 99999 |
| Previous phone | 619-353-4949 |
| Marital status | Widowed |
| Religion / Lang | Catholic / English |
| Race | White |
| Resident # | 15524 |
| Admitted from | Acute care hospital — **SCRIPPS MERCY CHULA VISTA** |
| Primary payer | Scripps Health Hosp Agrmt |
| Admitting physician | BHAVSAR, SHEILA (General Surgeon) |
| Other providers | Attending: Bhavsar, Sheila / Makovsky, Ken; Psychiatrist: Keri, Jason; Psychologist: Katyal, Radhika; On-Call: Baron, Annahita; It, Alan |
| Pharmacy | (Van Nuys, CA) |

### Contacts
| Name | Type | Relationship | Phone |
|---|---|---|---|
| PETRUCCIO, ELIZABETH TINA | Self | Self | — |
| DIMARELLO, ERIKA | Emergency Contact #1 | Daughter | (602) 802-3373 |
| DIMARELLO, ANTHONY | Emergency Contact #2 | Son | (567) 305-0494 |
| MARTINEZ, JOAN | Emergency Contact #3 | Sister | (609) 731-1541 |

## Page 2 — Diagnosis information (all onset 02/17/2024)
| # | Code | Description | Rank |
|---|---|---|---|
| 1 | M46.22 | **Osteomyelitis of vertebra, cervical region** | Primary |
| 2 | A41.9 | **Sepsis, unspecified organism** | 2 |
| 3 | I50.23 | Acute on chronic systolic (congestive) heart failure | 3 |
| 4 | R26.89 | Other abnormalities of gait and mobility | 4 |
| 5 | Z74.1 | Need for assistance with personal care | — |
| 6 | R13.10 | Dysphagia, unspecified | 6 |
| 7 | R41.841 | Cognitive communication deficit | 7 |
| 8 | J45.909 | Unspecified asthma, uncomplicated | 8 |
| 9 | I10 | Essential (primary) hypertension | 9 |
| 10 | I48.0 | Paroxysmal atrial fibrillation | 10 |
| — | J18.9 | Pneumonia, unspecified organism | Other |
| — | J96.02 | Acute respiratory failure with hypercapnia | Other |
| — | K12.30 | Oral mucositis (ulcerative), unspecified | Other |
| — | K80.20 | Calculus of gallbladder without cholecystitis without obstruction | Other |

## Page 2 — Miscellaneous / discharge
| Field | Value |
|---|---|
| Date of Discharge | **03/14/2024** |
| Time | 2256 (22:56) |
| Length of Stay | **26** days (02/17/2024 -> 03/14/2024; arithmetic confirms 26) |
| Discharged to (Mortician Name and Licence No.) | **Other: OTHER** |
| Signature / Date / Time | blank |
| Personal Effects Sent With / Relationship / Date / Time | blank |
| ADVANCE DIRECTIVE section | no content detected |

## Death claim — verification result
- **No explicit "died / deceased / expired / date of death" string was found** on either page by either OCR engine.
- The only death-adjacent elements are the static form labels:
  - "Discharged to (Mortician Name and Licence No.)" -> value entered reads **"Other: OTHER"** (no mortician named)
  - "Personal Effects Sent With" -> blank
- Therefore this face sheet, as far as its machine-readable content goes, documents a **discharge on 03/14/2024**, not a death. It does not confirm or deny death.
- If a death indicator exists on the page, it is likely a checkbox/tick or handwriting that pixel-OCR is not resolving. Needs visual confirmation of the exact wording/field.

## Corroboration note
- The earlier AI's claims of a **"bone infection"** and **"sepsis"** map onto this real primary source:
  M46.22 cervical vertebral osteomyelitis (primary) + A41.9 sepsis. Those specific claims are now **sourced**, not fabricated.
- `petruccio` was returning zero hits in prior sweeps only because this file was outside every searched path
  (it was in `Downloads\fwdfacesheet\`, now moved to `evidence\medical_records\raw\fwdfacesheet\`, dated 2026-09-30 17:38).
