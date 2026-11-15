# HBNC PERMIT MASTER MANIFEST
## Huntington Beach Navigation Center — 17631 Cameron Ln (assessor 167-472-08), Huntington Beach, CA 92647
### Also referenced as 17642 Beach Blvd / Cameron Lane / "Navigation Center - Mercy House"

**Compiled:** 2026-10-09
**Question answered:** which permits were pulled for HBNC inside the Google Drive "Construction Monitor" files?

---

## A. VERIFIED ANSWER

**Construction Monitor weekly OC files contain only 3 of the HBNC permits.** The complete set of **12 Building + 5 Fire + 1 Engineering** records was recovered by combining Construction Monitor with the prior live Accela pull (`live_accela_permits_exhaustive.json`, Drive id `11ZmQwlpnEqfHlBjZFNmymcu5wlXO7tgt`) and a full CapDetail processing-status pull on 2026-10-10.

### A1. Permits found IN the Construction Monitor files
Source dir: `C:\Amd949609_Antigravity_v1\cloud_storage\construction_monitor\oc_weekly_2020\`

| Permit | CM pmt_date | Description | Value | Builder | Source file |
|---|---|---|---|---|---|
| B2020004554 | 08/19/2020 | Demolition Dwelling | 16,000 | Macro-Z-Technology Company (Santa Ana) | `CA-oc-2020-41-all-2.csv` |
| B2020005184 | 10/28/2020 | Emergency Homeless Shelter (Public Buildings & Projects) | 1,146,200 | Parker Brown Inc (Canoga Park, lic 689613) | `CA-oc-2020-46-all-2.csv` |
| B2020005996 | 10/28/2020 | Tenant Improvement (Comm Rmdl/Addn/Int Fin) | 435,000 | Parker Brown Inc | `CA-oc-2020-46-all-2.csv` |

Architect of record (CM): **Richard D Van Diepen**, 517 Magnolia Ave #B, Modesto CA 95354.
Owner of record (CM): **City Of Huntington Beach** / **City Of Huntington Beach Civic Im**, 2000 Main St, Huntington Beach CA 92648.

### A2. Full HBNC record set verified LIVE against Huntington Beach Accela
Verified 2026-10-09 against `https://aca-prod.accela.com/cohb/Cap/CapHome.aspx` by **parcel number 167-472-08** (definitive, paginated to exhaustion), **address 17631 Cameron**, and **project-name wildcards `%MERCY%` / `%NAVIGATION%`**. All records below are at **17631 Cameron Ln** and, where the narrative is populated, explicitly tagged **"NAVIGATION CENTER - MERCY HOUSE"** pursuant to **Resolution 2019-22**.

#### A2.1 Building module — 12 records (parcel 167-472-08, complete)
| # | Permit | Date | Type | Scope (verbatim) | Status |
|---|---|---|---|---|---|
| 1 | B2020-004554 | 08/18/2020 | Residential Combo | DEMO (E) 800 SF SFD (METHOD OF DEMOLITION:TRACTOR) SEWER CAP OFF *** CITY JOB *** PERMIT EFFECTIVE 08/19/20 | Expired |
| 2 | CO2020-004554 | 08/18/2020 | Certificate of Occupancy | attached to the demolition record | (CO) |
| 3 | P2020-004978 | 09/04/2020 | Plumbing | PLUMB TO PROVIDE ROUGH IN FOR SITE ***** MERCY HOUSE ***** | Expired Plan Review |
| 4 | M2020-004979 | 09/04/2020 | Mechanical | MECH TO PROVIDE HVAC FOR AREA - SPRUNG STRUCTURE ONLY ***** MERCY HOUSE ***** | **Finaled** |
| 5 | E2020-004977 | 09/04/2020 | Electrical | ELEC FOR EMERGERNCY HOMELESS SHELTER; INCLDS LIGHTING FOR SPRUNG STRUCTURE & SITE LIGHTING | Pending |
| 6 | P2020-005035 | 09/09/2020 | Plumbing | DRY UTILITY PLAN FOR EMERGENCY HOMELSS SHELTER (GAS PIPING ONLY) | Expired Plan Review |
| 7 | B2020-005184 | 09/11/2020 | Building | SHELL ONLY - SPRUNG STRUCTURE BUILDING (DORMITORY) FOR EMERGENCY HOMELESSS SHELTER | Expired |
| 8 | CO2020-005184 | 09/11/2020 | Certificate of Occupancy | COFO IN B2020-005184 (Code Enf. note 2023: this was a **TEMPORARY** CO) | **Issued** |
| 9 | **B2020-005914** | 10/14/2020 | Building | INT T.I. FOR SPRUNG STRUCTURE BUILDING (DORMITORY) — cross-ref "SEE B20005445" | Pending |
| 10 | B2020-005995 | 10/19/2020 | Building | SHELL - OFFICE TRAILER 1-4 - FOUNDATION ANCHORAGE & STAIRS/RAMPS | Pending (Pay Fees Due) |
| 11 | B2020-005996 | 10/19/2020 | Building | INT T.I. FOR OFFICE TRAILER 1-4 | Expired |
| 12 | M2020-006464 | 11/06/2020 | Mechanical | MECH TO PROVIDE HVAC FOR TRAILERS ***** MERCY HOUSE ***** | **Finaled** |

#### A2.2 Fire module — 5 records (parcel 167-472-08 / project `%NAVIGATION%`)
| Permit | Date | Type | Scope | Status |
|---|---|---|---|---|
| F2020-005031 | 09/09/2020 | Detection-Communication | [RD 3915] INSTALL (N) BUILDING FIRE ALARM SYSTEM FOR (N) 11,526 SQFT SPRUNG STRUCTURE **NAVIGATION CENTER** | **Finaled** |
| F2020-005032 | 09/09/2020 | Fire Suppression | [RD 3915] INSTALL (N) FIRE SPRINKLERS & PIPING FOR (N) 11,526 SQFT SPRUNG STRUCTURE **NAVIGATION CENTER** | **Finaled** |
| F2020-006947 | 12/03/2020 | Detection-Communication | [RD 3416] INSTALL (N) 9 DEVICES IN (E) FIRE ALARM SYSTEM FOR INT T.I. FOR **** NAVIGATION CENTER - SLEEPING TRAILER | **Finaled** |
| FMF-023343 | 04/13/2021 | Master File | [RD 3416] NAVIGATION CENTER | Active |
| FW2025-0024 | 10/02/2025 | Fire Watch | Fire Alarm Malfunction | Complete |

#### A2.3 Engineering / Planning / Urban Runoff
| Permit | Date | Module | Detail | Status |
|---|---|---|---|---|
| **PWG2020-020** | 2020 | Engineering (parcel 167-472-08) | **Grading**, Work Location `17631 Cameron, Huntington Beach, CA` | **Final** |
| ADR-2020-0268 | 12/10/2020 | Planning (parcel 167-472-09) | Address assignment for the Navigation Center and all associated buildings | Approved |
| CON-12038 | 08/27/2020 | Urban Runoff (parcel 167-472-09) | Construction Site — "HB Navigation Center", `17642 Beach Blvd / 17631 Cameron Ln` | Closed |
| PWE2008-270 | 05/05/2008 | Engineering (parcel 167-472-09) | Repair sewer lateral, no fee for the city | Issued |
| FMF-023343 | 04/13/2021 | Fire | Master File [RD 3416] Navigation Center | Active |

Planning-module parcel search on `167-472-08` = **NO RESULTS** (the only Planning record sits on parcel …-09).

**Note on date conflict:** Construction Monitor `pmt_date` for B2020005184 = 10/28/2020 and B2020005996 = 10/28/2020, while Accela shows 09/11/2020 and 10/19/2020. Construction Monitor carries the published/finalized date; Accela carries the application/record date. Both are correct for their own field.

#### A2.1b Processing Status (live CapDetail pull, 2026-10-10)
Every Building/Fire record was opened at `https://aca-prod.accela.com/COHB/Cap/CapDetail.aspx?Module={m}&TabName={m}&capID1=...&capID2=...&capID3=...` and the hidden sub-tab divs `#tab-processing_status` / `#tab-related_records` were extracted. CAPIDs: B2020-004554=`20CV2/00000/03CHY`, CO2020-004554=`03VZI`, P2020-004978=`06U2N`, M2020-004979=`05M81`, E2020-004977=`04VS6`, P2020-005035=`06U2Q`, B2020-005184=`03CMI`, CO2020-005184=`03VZK`, B2020-005914=`03CRO`, B2020-005995=`03CSD`, B2020-005996=`03CSE`, M2020-006464=`05MCE`, PWG2020-020=`20ENG/00000/005ZM`, F2020-006947=`20CV2/00000/051AE`.

| Permit | Workflow chain (verbatim dates/actors) | Verdict |
|---|---|---|
| B2020-004554 | Routed 08/18/2020 by Joe Velasquez → Issued 08/19/2020 (AA CONV) → **Expired 12/20/2021** by Accela Administrator (Inspections + Closed) | Demo completed, then auto-expired |
| CO2020-004554 | All 5 steps blank | Auto-generated CO stub, never processed |
| E2020-004977 | Accepted 09/04/2020 by Sokar Kong → Electrical Review Complete 09/08, 09/17, 10/20/2020 by David Moreno → Plans Coordination **TBD** → Permit Issuance **blank** | **Never issued** — stuck at Plans Coordination |
| M2020-004979 / M2020-006464 | Finaled | Mechanical closed out |
| P2020-004978 / P2020-005035 | Expired Plan Review | Plumbing plan review abandoned |
| **B2020-005184** | Accepted 09/11/2020 by Sokar Kong → Building Review Complete 09/11 & 10/21/2020 by Eric Haghani → Planning Review Complete 10/02/2020 by Jason Kelley → Public Works Note 09/11/2020 → Fire Review Complete 09/21 & 10/21/2020 by Steve Eros → **Issued 10/28/2020** (AA CONV) → **Closed 01/21/2021** → **Expired 05/05/2022** by Accela Administrator | Issued, then closed, then auto-expired |
| **CO2020-005184** | All 5 workflow steps **blank** — no "Marked as Issued" event anywhere | **Issued flag set without any workflow action** (see D1) |
| **B2020-005914** | Accepted 10/14/2020 by **Melanie Woo** → Routed 10/14/2020 → everything downstream blank | **Never reviewed, never issued** — parked at plan review |
| **B2020-005995** | Accepted 10/19 & 11/05/2020 by Melanie Woo → Building Review Complete 11/05/2020 by Eric Haghani → Planning Review Note 11/05/2020, **Approved 03/15/2021 by Jason Kelley** → Public Works Note 11/05/2020 → Fire Review Complete 11/05/2020 by Steve Eros → Plans Coordination blank → Permit Issuance blank → Closed TBD | **Fully approved, never issued** (fees still due) |
| **B2020-005996** | Accepted 10/19 & 10/21/2020 by Melanie Woo → Fire Review Complete 10/21/2020 by Steve Eros → Building Review Complete 10/22/2020 by Eric Haghani → **Issued 10/28/2020** → **Expired 05/05/2022** by Accela Administrator | Issued, then auto-expired |
| **PWG2020-020** | Engineering Grading; record body is near-empty (no licensed professional, no narrative); status **Final** | Confirms the STORMTECH report's PW 20-020 |
| F2020-005031 / F2020-005032 / F2020-006947 | Finaled; F2020-006947 = 9 new devices in existing fire alarm for the sleeping trailer, National Fail Safe (Westminster, lic 329699), related to B2020-005914 | Fire life-safety fully closed out |

Staff initials decoded from the workflow actors: **`kongs` = Sokar Kong**, **`woom` / `WOOM` = Melanie Woo**, `VELASQUJ` = Joe Velasquez.

#### A2.1c Why "B20005445" exists — origin fully traced 2026-10-10
**The string lives in exactly one place in the world: the city-entered Project Description field of `B2020-005914`.**

> `INT T.I. FOR SPRUNG STRUCTURE BUILDING (DORMITORY)**** NAVIGATION CENTER - MERCY HOUSE **** PURSUANT TO RESOLUTION 2019-22*** SEE B20005445 FOR DAILY RESULTS***MD ENTERED BY: WOOM`

"WOOM" = permit technician **Melanie Woo**, who accepted the record on 10/14/2020. She typed "SEE B2000XXXX FOR DAILY RESULTS" as a standard cross-reference to the master/daily-report permit. She used the **same template correctly on three sibling records**:

| Record | Her cross-ref | Target exists? |
|---|---|---|
| E2020-004977 | `***SEE B20004554 FOR DAILY RESULTS***MD` | YES → B2020-004554 |
| B2020-005995 | `***SEE B20004554 FOR DAILY RESULTS***MD` | YES → B2020-004554 |
| B2020-005996 | `***SEE B20004554 FOR DAILY RESULTS***MD` | YES → B2020-004554 |
| **B2020-005914** | `*** SEE B20005445 FOR DAILY RESULTS***MD` | **NO — never issued** |

So `B20005445` is the **same truncation convention** (`B2020-005445` → `B20` + `005445`) applied to a number that was never issued. The "daily results" pointer on the dormitory interior permit is a dead link.

**Propagation chain** — third-party vendors copy the Accela description field verbatim, so the phantom number reappears in commercial property reports as if it were a real permit:
1. **Accela live portal** — `https://aca-prod.accela.com/COHB/Cap/CapDetail.aspx?Module=Building&TabName=Building&capID1=20CV2&capID2=00000&capID3=03CRO&agencyCode=COHB` (source of truth).
2. **EDR Building Permit Report** — file `788703620.PDF` (Drive `1vgl-pkef4OPsHZ4LJSTn0Dp_z8xvdGFf`), Environmental Data Resources Inc, 6 Armstrong Road, Shelton CT, inquiry **7887036.20**, dated 03 Feb 2025, data sourced from **BuildFax**; page 9 "TARGET PROPERTY FINDINGS" reproduces "SEE B20005445 FOR DAILY RESULTS".
3. **Property Report** for 17631 Cameron Ln — file `PropertyReport_17631_CameronLn.pdf` (Drive `1atZzRNCB-ljqgVAU_kaGe-b20RdGNsH_`), 38 pages, page 13, same narrative.

**Negative results proving it is not an independent record anywhere:**
- Accela permit-number search `5445`, `005445`, `B2020-005445` across **Building, Planning, Engineering, Fire, Urban Runoff** = "Your search returned no results" on all five modules (2026-10-10). Code Enforcement and Business Licenses have no permit-number field on their search forms.
- Building-module wildcard `B2020-00544%` returned the complete issued block **005440, 005441, 005442, 005443, 005448** — 005444–005447 were never issued.
- Wayback CDX `huntingtonbeachca.gov/*5445*` = **zero captures**; `records.huntingtonbeachca.gov/*` has captures, none containing 5445.
- No web index returns the string.

**Conclusion:** `B2020-005445` / `B20005445` is a **single typographical error by one permit technician on one record**, laundered into apparent authority by two commercial data vendors who republish Accela's free-text field without validating the referenced number against the permit register.

---

## B. SOURCE-BY-SOURCE VERIFICATION

| Source | HBNC hits | Detail |
|---|---|---|
| Construction Monitor weekly OC 2020 CSVs (18 unique files, pmt_date 08/03/2020–12/14/2020) | **3** | See A1. 388 unique Huntington Beach permits extracted; only 3 at 17631 Cameron Ln |
| Construction Monitor `permitinfo` 2020 broad CSV (15,992 rows, 12/02/2019–05/25/2020) | **0** | Date range ends before all HBNC permits |
| Construction Monitor `permitinfo*.csv` 2023 set (16,476 rows, 08/31–09/27/2023) | **0** | Wrong period |
| `Construction Monitor Permits.pdf` (11 MB, 1,477 pp, 08/31–09/27/2023) | **0** | 1,476 `Pmt#` refs; zero hits for Navigation/HBNC/17642/17631/Cameron/Mercy/Shelter/B2020005184 |
| `Construction_Monitor.zip` + `Construction_Monitor (1).zip` | 0 | Byte-identical to the 2020 permitinfo CSVs |
| **Live Accela pull** `live_accela_permits(_exhaustive).json` | **10** | First-pass address query (17631 Cameron) |
| **Live Accela parcel query 167-472-08** `C:\OsintNeoAi\data\accela_parcel_08_building_full.json` | **12** | Paginated to exhaustion 2026-10-09 — authoritative Building list (adds B2020-004554 + CO2020-004554, both on page 2) |
| **Live Accela parcel query 167-472-09** (17642 Beach Blvd) | **0 Building** | "Your search returned no results" — **no building permits exist under the Beach Blvd address** |
| **Live Accela Fire module** `C:\OsintNeoAi\data\accela_parcel_permit_search.json` | **5** | F2020-005031, F2020-005032, F2020-006947, FMF-023343, FW2025-0024 |
| **Live Accela Engineering module** | **1** | PWG2020-020 Grading, Final, 17631 Cameron |
| `Accela Citizen Access 17642 beach.pdf` (`evidence\hb_project_binder_16eX_20260906\Downloads\`) | 14 recs | MyCollection export for parcel **167-472-09**: 10 Code Enforcement, PWE2008-270, FMF-023343, ADR-2020-0268, CON-12038. No Building section |
| `stormtech_legal_permit_index.json` (226 permits) | **0** | Programmatic count: 17631=0, 17642=0, Cameron=0, Navigation=0, Mercy=0, and all 12 permit numbers =0. Confirms the STORMTECH report's own conclusion (zero HBNC StormTech permits in that index) |
| `STORMTECH_HBNC_PERMIT_FORENSIC_REPORT.md` (Drive `1EiZztYLm3XJrumwnDCvigHnXOf-MQo5T`) | lists 3 | Subpoena target #4 names B2020-005184, **B2020-005914**, B2020-005996 — all 3 now located |
| `hbnc_permit_urls.txt` (Drive `EVIDENCE_LOCKER_MASTER/09_PERMITS/`) | 0 permits | Only Navigation Center monthly Data Reports (Dec 2023–Mar 2025) + 2019 council presentations + 2020-11-02 ribbon-cutting press release |
| `permit_search_hits.txt` | local PDFs only | Keyword hits in `G:\buckp moto\Download\*.pdf` for 17631 Cameron / 17642 Beach — not permit records |

### Non-Construction-Monitor permits already on file for this project (from STORMTECH report)
PW# 20-020 (Public Works grading, Final), L# 20-128 (internal plan review docket), PWE2020-304 + PWE2022-0046 (encroachment, unverified), WDID 8 30W004769 (SWRCB erosivity waiver), OCHCA #20IC002 (health case), HBFD Spec #415 (fire lane).

---

## C. GAP STATUS (items 1 and 2 of the follow-on CLOSED 2026-10-09)

1. ~~**B2020-005445**~~ **CLOSED — permit does not exist.** Six query formats + wildcard block scan `B2020-00544%` prove 005445 was never issued. It is a clerical typo inside B2020-005914's narrative.
2. ~~**17642 Beach Blvd**~~ **CLOSED — zero Building records.** Parcel `167-472-09` Building-module search returns "Your search returned no results". The address carries only Code Enforcement (10), PWE2008-270, FMF-023343, ADR-2020-0268 and CON-12038, per the saved MyCollection PDF. The earlier `"Table missing or error."` was a page-load artifact, not a data gap.
3. **Construction Monitor 2020 week files missing:** weeks 1–5, 7–35, 48, 52 → no CM coverage for pmt_date 05/26/2020–08/02/2020 or 12/15/2020–12/31/2020. No `CA-oc-2021-1` or `CA-oc-2020-52` exists on Drive. **Impact on HBNC: none** — the live Accela parcel query is not date-bounded and returned the complete set.
4. **Construction Monitor is a filtered lead-gen subset**, not the full HB city ledger (B2020-005914 dated 10/14/2020 falls inside week-43 coverage yet is absent; 388 HB permits vs. hundreds per week in reality). Do not treat CM as an authoritative completeness source.

---

## C2. CERTIFICATE-OF-OCCUPANCY FORENSICS (closed 2026-10-10)

**D1 — The CO was issued against a permit that never had a permanent occupancy path.**
`CO2020-005184` shows Record Status **Issued**, yet its Processing Status tab has **all five workflow steps blank** (Application Submittal / Building Review / Inspections / Permit Issuance / Closed) — there is no "Marked as Issued" event. Its parent building permit `B2020-005184` **was** issued 10/28/2020, then **Closed 01/21/2021**, then **auto-Expired 05/05/2022**. Both records carry an identical Project Description that states in plain text:

> `*** COFO IN B2020-005184 ***`

i.e. the Certificate of Occupancy was filed **inside** the building permit record, and the separate CO record is a system-generated mirror. Code Enforcement note **CC2023-02189** (parcel 167-472-09, in the saved MyCollection PDF) independently confirms this was a **TEMPORARY certificate of occupancy that was never converted to permanent**.

**D2 — Nothing else on site ever obtained occupancy.** Of the four interior/shell permits:
- `B2020-005914` (dormitory interior TI) — never reviewed, never issued.
- `B2020-005995` (office trailer shell/foundation) — **fully approved 03/15/2021 by Jason Kelley**, fees still due, never issued.
- `B2020-005996` (office trailer interior TI) — issued 10/28/2020, **expired 05/05/2022**.
- `E2020-004977` (electrical) — reviews complete 10/20/2020, **never issued**.

Only the **mechanical** permits (`M2020-004979`, `M2020-006464`) and all three **fire** permits reached **Finaled**. So as of the live 2026-10-10 pull: the shelter's life-safety systems are finaled, its HVAC is finaled, its grading is Final, but **the building itself is operating on a temporary CO attached to a permit that has since expired**.

**D3 — Related-record tree.** `CO2020-005184` links to `B2020-005184`, `CO2020-005184`, and **`FMF-023343` (Master File, "[RD 3416] NAVIGATION CENTER", 04/13/2021)** — the Master File is the Fire Department's umbrella record and is still **Active**. `B2020-005914` links to `F2020-006947` (fire alarm, sleeping trailer). `B2020-005995`, `B2020-005996` and `E2020-004977` have **no related records** — the office-trailer and electrical permits were never linked into the HBNC tree.

### Still open (queued in `backlog_tasks.md`)
- ~~Capture status detail for the Building-module records~~ **CLOSED 2026-10-10** — see A2.1b and C2.
- Pull plan sets for PWG2020-020 (confirmed live, Final, CAPID `20ENG/00000/005ZM`) from Laserfiche folder 4806972 / docs 5406552 & 6386715 to reconcile the StormTech grading claims — **BLOCKED**: `https://records.huntingtonbeachca.gov/WebLink/DocView.aspx?id=5406552&dbid=0&repo=COHB` and every other WebLink URL return a connection timeout (WinError 10060) from this network. Needs a session from an unblocked egress.
- Accela attachment lists (approved plan sets, correction lists, issued-permit PDFs) render inside a lazily-populated iframe on CapDetail; direct `AttachmentsList.aspx` requests return an empty body. Requires a click-to-load pass.
- Code Enforcement records for parcel …-08 (module search form lacks the parcel field; 10 records already captured in the MyCollection PDF for …-09).

---

## D. LOCAL FILE INDEX (this work)

- `...\cloud_storage\construction_monitor\oc_weekly_2020\` — 22 downloaded weekly CSVs
- `...\cloud_storage\construction_monitor\live_accela\live_accela_permits_exhaustive.json` (7,750 B)
- `...\cloud_storage\construction_monitor\live_accela\live_accela_permits.json` (5,660 B)
- `...\cloud_storage\construction_monitor\STORMTECH_HBNC_PERMIT_FORENSIC_REPORT.md` (9,543 B)
- `...\cloud_storage\construction_monitor\stormtech_legal_permit_index.json` (69,405 B, 226 permits)
- `C:\OsintNeoAi\data\accela_parcel_permit_search.json` — parcel / permit-number / project-name query results
- `C:\OsintNeoAi\data\accela_parcel_08_building_full.json` — paginated 12-record Building list (authoritative)
- `C:\OsintNeoAi\data\accela_permit_5445_search.json`, `accela_4554_search.json` — negative/positive proof queries
- `C:\OsintNeoAi\data\accela_5445_crossmodule.json` — 5445 re-checked across Building/Planning/Engineering/Fire/UrbanRunoff (all no-results)
- `C:\OsintNeoAi\data\accela_record_details.json` — per-permit CapDetail summary (type, status, url, CAPID)
- `C:\OsintNeoAi\data\accela_cap_details_full.json` — full processing-status / related-records / attachments text for all 16 records
- `C:\OsintNeoAi\scratch\detail_*.txt` — one normalized CapDetail text dump per permit
- `C:\OsintNeoAi\scratch\tabs_*.json` — same, structured
- `C:\OsintNeoAi\evidence\hb_project_binder_16eX_20260906\Downloads\Accela Citizen Access 17642 beach.pdf` — parcel 167-472-09 MyCollection export
- `C:\OsintNeoAi\backups\hbnc5445_*` — pre-edit backups of the three task-system files
- Tools: `C:\OsintNeoAi\skills\deep-osint\scripts\gdrive_search.py`, `gdrive_fetch.py` (copies in `C:\Amd949609_Antigravity_v1\scripts\`)
- Tools: `C:\OsintNeoAi\tools\accela_parcel_permit_search.py` (parcel/permit/project search, form-reset + no-results detection), `accela_record_details.py`, `accela_scraper.py`, `accela_scraper_exhaustive.py`; scratch query scripts in `C:\OsintNeoAi\scratch\`
- Root: `C:\Amd949609_Antigravity_v1\`


---

## E. GOOGLE PHOTOS EVIDENCE HARVEST (closed 2026-10-10, Law 3)

**Directive:** passive OSINT only — no city inquiry, no tip-off.
**Method:** Chrome DevTools Protocol (raw HTTP + websocket-client). `playwright.chromium.connect_over_cdp` hangs (leftover sessions + Google RotateCookiesPage interstitials) — do not reuse.
**Corpus:** user Google Photos (amd949609), searched via `https://photos.google.com/search/{q}`.
**Root:** `C:\OsintNeoAi\evidence\gphotos_hbnc\`

### E1. VERIFIED HIT — Temporary Certificate of Occupancy (PRIMARY)

| Field | Value |
|---|---|
| Document | TEMPORARY CERTIFICATE OF OCCUPANCY |
| Cert Number | **CO2020-005184** |
| Permit Number | **B2020-005184** |
| Site | NAVIGATION CENTER / MERCY HOUSE, 17631 CAMERON LN, HUNTINGTON BEACH CA 92647 |
| Printed / TCO Issue | **12/04/2020** |
| TCO Expiration | **06/04/2021** |
| Approved Sq Ft | 11,000.00 |
| Occupant Groups | B OFFICE, R-2, U STORAGE |
| Conditions | TEMPORARY CO ONLY — PURSUANT TO **RESOLUTION 2019-22**; TCO **EXCLUDES OVERFLOW TRAILER**; outstanding Public Works / Fire / Building inspection corrections shall be completed and approved prior to issuance of permanent Certificate of Occupancy |
| Owner | CITY OF HUNTINGTON BEACH, 2000 Main St, HB CA 92646, (714) 375-5348 |
| Dept | Planning & Building, (714) 536-5241, fax (714) 374-1647 |
| Photo ID | `AF1QipOKN9L86If_IVvnHLEQ5GlkQxMha3ozDkiB_7kl` |
| Local copies | `docs\d00_AF1QipOKN9L86If_IV.png`, `docs\TCO_CO2020-005184_photo.png`, `grading\tco_full.png`, `grading\tco_clip.png` |

**On-site posting photo (secondary):** `docs\d02_AF1QipO5XRSG7nNyBH.png` — same TCO taped beside an EXIT sign on-site, confirming physical posting of the temporary certificate at the facility.

**Corroborates:** Accela CapDetail (CO2020-005184 Status=Issued, all five workflow steps blank, description `*** COFO IN B2020-005184 ***`); Code Enf. note CC2023-02189 (temporary CO never converted); B2020-005184 expired 05/05/2022. **The building is still operating on a temporary CO that expired 06/04/2021.**

### E2. VERIFIED HIT — PRECISE GRADING PLAN sheet

Photo of a printed grading plan sheet titled:
- **PRECISION/PRECISE GRADING LANE — 17631 CAMERON LANE** (plan title block says 1761 in one crop; address line of TCO and all Accela records = 17631)
- EMERGENCY HOMELESS SHELTER
- 25 ABANDONED WELL LOCATION; WELL-PUMP ON CONCRETE BASE / PUMP HOUSE
- 400 FT N OF NEIMAN AVE; NAVBURN AVE / CAMERON ST
- Scale 1"=50'; BLDG. PMT # TBD (pre-permit plan state)
- **PW# still cropped off** in every capture — photo is a phone screenshot cut at the right edge (`aerial_fullres.jpg` = 672x1536; zoom crops of title-block strip do not contain the PW digits)

Photo IDs:
- aerial: `AF1QipOZnWZuABclW-4vKQlpbHwcUqHvGBw3BrGd5-sl` → `g_31`, `full_plan_aerial.png`, `aerial_fullres.jpg`
- B&W clean: `AF1QipN_KMNo4D_iwHqsL-Qb9kgmkp_C8bEtW8PS5iPc` → `full_plan_bw.png`
- clean: `AF1QipPALzvrNF5ddDdaDbqeXgv-Y6sSOKYKRCMX1lVv` → `g_29`, `full_plan_clean.png` (full-res of this ID via in-page fetch resolved to the well sketch — see E3)

**Engineering module live Accela already confirms PWG2020-020 Grading, Status Final, 17631 Cameron (CAPID 20ENG/00000/005ZM).** The photo is the physical plan sheet; full PW number on the sheet remains unreadable due to screenshot crop.

### E3. VERIFIED HIT — Well sketch (CSTB)

Filename/title in Photos viewer: **"well cameron CSTB+14..."**
- **Survey #5103**, **Well #1163**, **T8-129-11** (Tract / Block-Parcel)
- CAMERON ST parcel detail; hand-drawn site plan of the abandoned well + pump
- "well pump on a concrete12in pump base"; 1000 Gal tank & pump notes
- Street grid: BEACH BLVD / CAMERON ST / NAVBURN AVE / NEWLAND ST; TB-129-66, TB-129-82
- Local: `clean_fullres.jpg` (79,574 b), `full_well_sketch.png`, `c00_AF1QipMOah8vwFx1YR.png` (rotated phone view of same sheet)

**CSTB** = County Surveyor Tie Book (Orange County Surveyor document type). Only one such photo found; ocgis.com OCPW Associated Documents Map already returned "0 of 0 entries" for this parcel — ocgis is a dead end for city permit plans.

### E4. FALSE POSITIVES / NOISE (do not re-harvest)

Searches for "PRECISE GRADING LANE", "1761 CAMERON LANE", "CSTB", "TCO", "PWG2020-020", "PWG2020" produced heavy false positives. Confirmed noise (visual triage, Gemini vision 429 so `read` tool only):
- HP Pavilion P6000 box photo, Li-ion battery pack, skateboard / Barry's Boot Camp mural, CreditWise inquiries widget, federal resume book pages, CarGurus Audi listing, 1999 Upper Rim Rock Rd map pin, Rancho Huntington Lease mobilehome agreement (generic Mobilehome Residency Law text — **not** HBNC site docs; only matched "Huntington" string)

Remaining untriaged screenshot dumps left on disk for future re-scan if needed:
`g_00..g_34`, `n_00..n_18`, `p_00..p_11`, `c_00..c_14`, `v_00..v_17`, `docs\d01..d19`.

### E5. TOOLING (Law 1 + Law 10)

| Script | Purpose | Deposit |
|---|---|---|
| `gphotos_rawcdp.py` | Raw CDP template: `requests.put("http://127.0.0.1:9222/json/new")` → `websocket.create_connection(page_ws_url, suppress_origin=True)` → Page.navigate / Runtime.evaluate / Page.captureScreenshot | `C:\Amd949609_Antigravity_v1\scripts\gphotos_rawcdp.py` |
| `gphotos_fullres.py` | In-page credentialed fetch of `https://photos.fife.usercontent.google.com/pw/...` + btoa → full-res JPEG. Direct Invoke-WebRequest = **403** | `C:\Amd949609_Antigravity_v1\scripts\gphotos_fullres.py` |

Class-name gotcha: do not name a class `CDP` if a `CDP = "http://..."` URL constant exists — use `CDPClient`.
Search URL: space → `%20`. Tiles: `a[href*="/photo/"]`. Photo page: `https://photos.google.com/photo/{id}`.

### E6. STILL BLOCKED / OPEN

- **PW# on grading plan sheet** still cropped. Needs a differently-framed photo of the same sheet, or a zoom/pan pass inside the full-res Photos viewer image via raw CDP. Expect `PWG2020-020` per live Accela.
- Laserfiche `https://records.huntingtonbeachca.gov/WebLink/` still WinError 10060 from this network (docs 5406552, 6386715, 5401659).
- Accela CapDetail attachment iframe still needs a click-to-load pass.
- Gemini vision API quota 429 — use `read` tool for visual triage.

### E7. PW# RECOVERY PASS — CLOSED (source-exhausted, 2026-10-10)

**Goal:** recover the full PW digits cut off the grading-plan title block ("PW# 2..." then edge).

**Negative results (do not re-run the same methods):**
1. **Photos full-res of known plan IDs** — `aerial_fullres.jpg` is 672x1536; the phone screenshot itself is cropped at the right edge. Zoom/LANCZOS of title-block strip does not invent digits that are not in the source bitmap. B&W and clean full-plan shots (1920x851) are also left-edge phone crops of the viewer.
2. **Alternate-framing Photos search** — 20 queries (PWG2020-020, PWG2020, 20-020 grading, precise grading plan Cameron, L#20-128, PWE2020-304, 25 abandoned well, 1761 Cameron, BUILDING PMT, etc.) yielded 603 unique photo IDs. First 10 opened = all false positives (GEICO insurance card, DMV registration, Carrera GO toy, GPX projector box, CEP power box). Google Photos keyword search is too loose for permit numbers. Meta: `grading\pw_search\pw_search_meta.json`.
3. **Accela public CapDetail PWG2020-020** — full HTML dump `accela\pwg_capdetail_full.html` (193,465 b). Visible public fields only: Record Information PWG2020-020 / Grading / Record Status Final / Work Location 17631 Cameron. The Description textarea (`ctl00_PlaceHolderMain_addForDetailPage_txtDesc`) is an empty add-to-collection form control, not a project narrative. CapMoreDetails.aspx / CapPrint.aspx / CapRecordInfo.aspx = "file does not exist" on this Accela build.
4. **Accela AttachmentsList.aspx Engineering CAPID 20ENG/00000/005ZM** — "No records found." Same for Building/Fire CAPIDs previously pulled. Public portal does not expose plan-set PDFs for these records.
5. **Laserfiche via Chrome browser** (same network, browser path) — `records.huntingtonbeachca.gov` home + DocView 5406552 + 6386715 all `ERR_CONNECTION_TIMED_OUT`. Confirms block is network egress, not Python-only.
6. **ocgis.com OCPW Associated Documents Map** — already "0 of 0 entries" for this parcel (county surveyor docs only).

**Working conclusion:** the grading-plan photo is consistent with Accela **PWG2020-020** (shows "PW# 2…" then cut) and STORMTECH's **PW# 20-020** claim. Full printed digits are not recoverable from any current public or local source on this network. Laserfiche remains the only known host of the official plan set; needs unblocked egress.

**Chrome CDP note:** default-profile Chrome relaunched with `--remote-debugging-port=9222` (PID 18440 at launch). Dedicated-profile Chrome without cookies dies / cannot auth Accela. Always use default profile for ACA + Photos sessions.

**Scripts deposited (Law 10):** `gphotos_pw_search.py`, `accela_pwg_attach.py`, `accela_more_urls.py` in `C:\Amd949609_Antigravity_v1\scripts\`.

### E8. ACCela ENGINEERING + CODE ENFORCEMENT PASS (2026-10-10) — NEW EVIDENCE

**Method:** Chrome CDP default-profile session against https://aca-prod.accela.com/COHB/ — CapHome General Search per module; result-table CapDetail click-through; force-visible tab panels on CapDetail. Artifacts: `evidence\gphotos_hbnc\accela\search_*.txt/png`, `eng_cameron_fullrows.txt`, `eng_cameron_p1p2.txt`, `eng_cameron_rows_p1p2.json`, `enf_parcel08.txt`, `enf_parcel08_p2.txt`, `enf_17631_cameron.txt`, `*_capdetail.txt/html/png`, `module_search_pass2.json`–`pass5.json`, `enf_details_pass5.json`, `pwg020_capdetail_dom.html`.

#### E8.1 Engineering records at 17631 Cameron / parcel 167-472-08
| Record | Type | Status | Description / notes | Work Location |
|---|---|---|---|---|
| **PWG2020-020** | Grading | **Final** | (prior work) grading for navigation center | 17631 Cameron |
| **PWE2020-304** | Encroachment | **Final** | "Set construction trailer in ROW for **City Homeless Shelter project**." (search date 09/17/2020) | 17631 Cameron |
| **PWE2020-331** | Encroachment | **Issued** | Install new gas service; asphalt cuts; Not# 30218391-5431210 (10/01/2020) | 17631 Cameron |
| **PWE2022-0046** | Encroachment | **Final** | "Project 20211195-G4155. **5 Borings** in property, not in street. **4 story building 1.58 Acre lot**." (01/25/2022) | 17631 Cameron Lane & **17624 Beach Blvd** |

Adjacent Cameron records (NOT HBNC, confirm parcel-adjacency only): PWG2021-0071 / PWMM19154 tract 19154 18-unit condo at 17532 Cameron Ln; PWG2024-0018 ADU at 17682 Cameron; PWE2023-0241 SCE OH-UG Shea Homes; PWE2022-0575 cable work 17532 Cameron. Engineering street search "Cameron" = 21 results (pages 1–2 complete).

Public CapDetail for PWG2020-020 / PWE2020-304 / PWE2020-331 / PWE2022-0046: Record Info collapsed; Work Location + Status only; tab-attachments / tab-related_records / tab-conditions exist in DOM but empty for anonymous user. AttachmentsList.aspx still "No records found." Laserfiche still TCP-blocked (192.5.222.218 ports 80+443 dead from this egress).

#### E8.2 Code Enforcement — parcel 167-472-08 (16 records, pages 1–2 complete)
All CapDetail URLs under Module=Enforcement. Public Descriptions are full text.

| Record | Type | Status | Date | Description (public) | Location on CapDetail |
|---|---|---|---|---|---|
| CV20190044207 | Enforcement Violation | Closed | 2019 | Homeless living on the property, faulty weather protection, overgrown/dead vegetation | **17631 Cameron Ln** |
| CC20120093205 | Code Complaint | Closed | 2012 | HOMELESS LIVING ON PROPERTY. MATTRESS AND OTHER DEBRIS. VISUAL BLIGHT. HOMELESS USE COMPLAINANT ADDRESS AS 'BATHROOM' - REFERRED TO HBPD | **17631 Cameron Ln** |
| CC2022-00278 | Code Complaint | Case Generated | 01/14/2022 | Fence covered with cloth used for graffiti; shelter area blight; more police patrol at night. Related CV2022-00360 | 17642 Beach Blvd |
| CV2022-00360 | Enforcement Violation | Unfounded | 01/21/2022 | Same graffiti/fence text | 17642 Beach Blvd |
| **CC2022-05921** | Code Complaint | **Referred** | ~Aug 2022 | **HB NAVIGATION CENTER •IS THERE A NO AC LAW? •WATER FOUNTAINS DO NOT WORK PROPERLY AND THE WATER DOESN'T TASTE FRESH AND HEALTHY •PROPERTY SMELLS LIKE PEE AND POOP •PROPERTY IS TOO DARK AND UNSAFE SECURITY DOESN'T PROTECT THE GUESTS THEY ALLOW PROBLEMS TO GO ON AT THE SHELTER AND THEY WATCH AND LAUGH** | **17642 Beach Blvd** |
| **CC2022-05944** | Code Complaint | **Referred** | ~Aug 2022 | Same NO AC / water / smell / darkness / security text + **"See email in Documents."** | parcel -08 list |
| **CC2023-01632** | Code Complaint | **Case Generated** | 03/14/2023 | received call from OC social worker for patient Complaint is regarding navigation center. **Seems that there is feces and mold on the walls inside.** Related CV2023-01635 [RD 3416] | parcel -08 list |
| **CV2023-01635** | Enforcement Violation | **Referred** | 03/14/2023 | Same feces/mold text | parcel -08 list |
| **CC2023-02189** | Code Complaint | **Unfounded** | 04/05/2023 | See Supervisor. **CO2020-005184** (17631 Cameron Ln) was a **Temp. Certificate of Occupancy**. Need to verify if business is still at location and work with business to obtain **permanent Certificate of Occupancy** | parcel -08 list |
| CC2024-02522 | Code Complaint | Unfounded | 05/03/2024 | "sdd" (noise) | parcel -08 list |
| CV2024-06507 | Enforcement Violation | Resolved | 11/09/2024 | Graffiti on the electrical box behind the homeless shelter | parcel -08 list |
| CC2024-06913 | Code Complaint | Unfounded | 12/02/2024 | lots of trash at homeless shelter on the **Newman side** of complex | parcel -08 list |
| CC2025-04241 | Code Complaint | Referred | 09/24/2025 | MyHB #2938433 Graffiti on Cameron Ln by green electrical box (photo in docs) | parcel -08 list |
| **CC2026-01002** | Code Complaint | **Referred** | 03/02/2026 | **"I am requesting an inspection and written determination regarding an apparent lack of required ventilation and inconsistent conditioned air at the Huntington Beach Navigation Center (City-operated shelter facility). I am currently residing in the dormitory sleeping area."** See email in Documents. | **17642 Beach Blvd** |
| **CC2026-01328** | Code Complaint | **Case Generated** | 03/20/2026 | **No conditioned or ventilation air observed in dormitory sleeping area or restroom/shower spaces. Possible violation of 2022 CBC §1202.1/§1202.5 and 2022 CMC §402.1. Request inspection and determination of required corrective actions.** Related CV2026-01406. Attachment upload UI present (public upload form; files not listed anonymously). | parcel -08 list |
| **CV2026-01406** | Enforcement Violation | **Resolved** | 03/25/2026 | Same CBC/CMC ventilation text | parcel -08 list |

Street-no search 17631+Cameron on Enforcement = only the 2 pre-shelter records (CV20190044207, CC20120093205). Parcel-based search is the correct key for the shelter-era cases.

#### E8.3 Analytic notes (passive only)
- **Living-shelter health/safety complaints are still open into 2026:** ventilation/AC in dormitory + restroom/shower cited against 2022 CBC §1202.1/§1202.5 and 2022 CMC §402.1 (Mar 2026). CV2026-01406 marked Resolved but parent CC2026-01328 remains **Case Generated**; CC2026-01002 remains **Referred**.
- **TCO-to-CO gap still on the books:** CC2023-02189 (Unfounded disposition) explicitly documents CO2020-005184 as Temp CO pending permanent CO — corroborates prior master finding that the TCO was never converted (CC2023-02189 + no permanent CO in Accela).
- **Beach Blvd frontage:** HBNC CapDetails for 2022/2026 complaints list Location **17642 Beach Blvd** (not 17631 Cameron). Parcel 167-472-08 search still returns them — multi-address CAP.
- **2019/2012 records** prove the Cameron address was already a known homeless encampment site **before** the navigation center opened.
- **PWE2022-0046** 5 borings / 4-story / 1.58 acre at 17631 Cameron + 17624 Beach is consistent with post-TCO site evaluation or adjacent Beach parcel work; do not assume it is a second HBNC building permit without Laserfiche plan set.
- Public CapDetail attachments remain gated; "See email in Documents" on CC2026-01002 and CC2022-05944 are **not** downloadable anonymously.

**Do not re-run** CapHome parcel/street searches for the same modules — results are cached in this section and on disk.
