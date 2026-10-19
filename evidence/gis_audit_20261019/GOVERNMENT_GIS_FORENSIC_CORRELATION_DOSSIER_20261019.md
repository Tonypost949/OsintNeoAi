# GOVERNMENT GIS FORENSIC CORRELATION DOSSIER
## Ghost-Maintenance / Falsified-Layer Analysis Applied RICO-Wide
### Huntington Beach Navigation Center (HBNC) Corridor — Primary Case Study

**Report date:** 2026-10-19
**Classification:** Federal Relator Work Product / Qui Tam Investigative Record
**Prepared by:** NEO (autonomous OSINT agent)
**Companion manifest:** `public_repo/OsintNeoAi-Public/GIS_SOFTWARE_AND_MUNICIPAL_INFRASTRUCTURE_AUDIT_MANIFEST.md` (commit `cd053901b1ea6c2c8e1eac0c6cb57b8a20741725`)
**Evidence workspace:** `/home/osintneoai/evidence/gis_audit_20261019/`

**Evidence grades used throughout:**

| Grade | Meaning |
|---|---|
| **[VERIFIED]** | Live REST query or official record returned the stated value; query URL/reproducible recipe included. |
| **[INFERRED]** | Multiple verified data points support the conclusion, but no single record proves it. |
| **[UNVERIFIED]** | Claim exists in prior work product; not independently confirmed in this pass. |
| **[OSINT ARTIFACT]** | Locally authored visualization/analysis, not a municipal record. Cannot be cited as government data. |

---

## 0. EXECUTIVE FINDINGS

1. **[VERIFIED] The City of Huntington Beach exposes an authoritative address layer with public write capability.** `AddressEdits/FeatureServer/0` advertises `Query,Create,Update,Uploads,Editing`. No credentials are required to query it; write authentication was **not** tested because altering a government record is prohibited. This is the single most serious GIS integrity exposure found.
2. **[VERIFIED] 99.99% of the address layer was rewritten by one account in mass events.** Of 99,804 address records, **99,791** carry `last_edited_user = SPRADLIA`. **83,641** share a single timestamp (2026-01-29 22:14:02 UTC) and another **9,704** share 2025-03-25 15:14:37 UTC. Creation metadata is blank on **89,691** records. Per-record provenance for the city's address fabric has been erased.
3. **[VERIFIED] 100% of the parcel layer was re-saved under one account between March and July 2026.** `NUWEYT` is `last_edited_user` on **52,081 of 52,081** parcels (51,830 distinct APNs), in machine-timed batches (2026-03-03, 2026-04-09/10, 2026-07-23/24).
4. **[VERIFIED] 100% of the sanitary sewer pipe and lateral fabric was re-saved under the same account.** Sewer pipes: **8,542/8,542** NUWEYT; laterals: **49,482/49,482** NUWEYT; manholes: 8,333/8,349; sewer features: 12,049/12,219. Pipe timestamps cluster 2026-08-13 05:06–05:17 UTC, i.e. a single overnight bulk load.
5. **[VERIFIED] The 2024 OCTA trash-capture grant inventory is 100% NUWEYT-stamped.** All **66/66** assets in `StormwaterBMPs/MapServer/14` carry `last_edited_user = NUWEYT` (2026-05-15). This is the grant-credit layer: if an asset cannot be physically located, the grant claim is unsupported.
6. **[VERIFIED] The HBNC address-to-parcel crosswalk is internally inconsistent.** The address point `17642 Beach Blvd` is attached to **APN 167-472-08**, but the parcel layer and the Orange County Assessor both assign 17642 Beach Blvd to **APN 167-472-09** (Lot 7, Tract 405); APN 167-472-08 is 17631 Cameron Ln (Lot 6). Any address-to-parcel join for the shelter returns the wrong lot.
7. **[VERIFIED] The HBNC parcels are owned by the Huntington Beach Housing Authority**, mailed to 2000 Main St (City Hall). The two lots are Lots 6 and 7 of Tract 405, with 2020/2021 documentary references. Both parcels were last edited by NUWEYT on 2026-04-09 21:11 UTC.
8. **[VERIFIED] The site is zoned SP14 (Specific Plan) with General Plan `M-sp` (Mixed Use–Specific Plan)** — not a residential zone. The shelter address is nevertheless classified `Residential` in the address layer.
9. **[VERIFIED] The County of Orange's independent stormwater fabric carries no human editor attribution.** In the HBNC corridor, **124/124 inlets** and **174/174 gravity mains** are stamped `ARCGISADMIN` (2018-09-28 and 2020-05-15 respectively); all 174 main invert fields are null. The county cannot demonstrate per-asset human review from this service.
10. **[VERIFIED] Both custodians' storm/sewer fabrics therefore lack usable per-asset audit provenance** — HB because of the 2026 NUWEYT bulk load, OC because of 2018/2020 system migration stamps. This is an accountability vacuum, not by itself proof of intent.
11. **[VERIFIED] Possession of cracked Esri installers is documented; execution/use is not.** The audit manifest lists ArcGIS 10.2 License Manager + Crack, ArcGIS Desktop 10.8.2, Esri ArcGIS 10.7.1, and ArcGIS Pro 3.1.5 in a Downloads archive. No `.mxd`, `.aprx`, `.shp`, `.gdb`, license-manager log, Prefetch, Amcache, or registry artifact is present in this workspace. Claims that pirated ArcGIS "built" a specific municipal product remain **[UNVERIFIED]** pending those artifacts.
12. **[OSINT ARTIFACT] The "2,247 cu ft StormTech" figure is not a municipal record.** It appears only in the locally authored `hbnc_rico_gis.html`. The permit-derived plan figures are 10 × MC-3500 chambers = **1,099 ft³ nominal / 1,789 ft³ minimum installed** (109.9 / 178.9 ft³ each). The HTML also plots the chamber field along a ~1 km line west of the site. It cannot be used as evidence of what the city built.

---

## 1. THE GHOST-MAINTENANCE FORENSIC LOGIC

The HBNC hypothesis is that infrastructure condition, maintenance, and grant-credit records were represented as complete when the underlying assets were absent, unmaintained, or misdocumented. Applied generically to any government GIS, the test is:

| # | Test | Question | Failure signature |
|---|---|---|---|
| T1 | **Ghost ticket** | Does each asset have a work order, inspection, date, human, and cost? | Asset exists in GIS; no corresponding maintenance/inspection record. |
| T2 | **Editor attribution** | Is `last_edited_user` a named person, a system account, or null? | `ARCGISADMIN`, `SA`, null, or a bulk account. |
| T3 | **Write exposure** | Can the authoritative layer be edited anonymously? | `Create/Update/Delete/Editing` in public capabilities. |
| T4 | **Provenance destruction** | Are creation fields populated and preserved? | `created_user`/`created_date` null or overwritten. |
| T5 | **Bulk-event detection** | Were many records changed in identical seconds? | Thousands of records sharing one timestamp. |
| T6 | **Cross-jurisdiction differential** | Does an independent custodian's layer agree? | County vs. city geometry/attribute mismatch. |
| T7 | **Official-record reconciliation** | Do assessor, recorder, permit, and grant records agree with GIS? | Parcel/address/owner/permit crosswalk mismatch. |
| T8 | **Capacity-claim test** | Do hydraulic/capacity attributes match as-builts and inspections? | Design volume/capacity asserted without as-built or inspection support. |

A finding of T2/T4/T5 failure is an **accountability** finding. It becomes a **fraud** finding only when paired with T1, T7, or T8 and a specific misrepresentation.

---

## 2. CITY OF HUNTINGTON BEACH GIS (PRIMARY NODE)

### 2.1 Platform inventory

- **Host:** `gis.huntingtonbeachca.gov` → `192.5.222.153` (City-owned AS393281, no WAF per RICO matrix).
- **Software:** self-hosted Esri ArcGIS Server (MapServer/FeatureServer/GeocodeServer/GPServer/SymbolServer).
- **Live enumeration:** **43 services, 584 layers.** 27 services are versioned. **159 layers carry editor-tracking fields.** Only **one** service is write-enabled: `AddressEdits`.
- **Full metadata capture:** `/home/osintneoai/evidence/gis_audit_20261019/hb_arcgis_services_full.json` (1.09 MB).
- **Key services:** `Parcels`, `AddressEdits`, `Planning`, `PublicWorks`, `SewerLayers`, `SewerBroadcast`, `StormLayers`, `StormBroadcast`, `StormwaterBMPs`, `SurfaceFlow`, `Property`, `WebFire`, `WebPolice`, `BusinessAnalysis`, `Transportation`, `WaterBroadcast`, `UtilitiesBaseMap`, plus historical orthophoto services.

### 2.2 Public write exposure — `AddressEdits`

**[VERIFIED]** Service capabilities: `Query,Create,Update,Uploads,Editing`. Layer capabilities: identical. Versioned: `true`. Editor tracking fields are configured (`created_user`, `created_date`, `last_edited_user`, `last_edited_date`).

| Metric | Value |
|---|---|
| Address records | 99,804 |
| `last_edited_user = SPRADLIA` | 99,791 |
| `last_edited_user = SA@SQL57.HUNTINGTON` | 12 |
| `last_edited_user = NUWEYT` | 1 (6463 Overlook Dr — unrelated to HBNC) |
| Records with `created_user = null` | 89,691 |
| Records sharing 2026-01-29 22:14:02 UTC | **83,641** |
| Records sharing 2025-03-25 15:14:37 UTC | **9,704** |
| Distinct SPRADLIA timestamps | 406 (through 2026-10-13) |

**Interpretation [INFERRED]:** the 2025 and 2026 events were layer-wide re-saves (schema change, migration, or bulk update), not individual edits. They destroyed the distinction between records that were genuinely changed and records that were merely rewritten. The layer was still being edited as of 2026-10-13, so it is a live operational layer, not a frozen archive. Because it is publicly writable, an anonymous actor could also alter an address and inherit the same undifferentiated timestamp pattern.

### 2.3 Parcel fabric — 100% NUWEYT

**[VERIFIED]** `Parcels/MapServer/0` contains 52,081 features. Query `DATA.Parcels.last_edited_user='NUWEYT'` returns the entire layer when paged: **52,081 records, 51,830 distinct APNs**.

| Edit window (UTC) | Records |
|---|---|
| 2026-03-03 15:30–15:35 | 1,131 |
| 2026-04-09 21:11–21:12 | 4,538 |
| 2026-04-09 23:09–23:50 | 22,625 |
| 2026-04-10 15:20–15:38 | 23,531 |
| 2026-07-23/24 | 256 |
| **Total** | **52,081** |

**Interpretation [INFERRED]:** this is an assessor-roll load / parcel-fabric refresh executed under a single login. It is consistent with a scheduled data integration. It is **not** evidence that the HBNC parcels were singled out. However, it means the current parcel attributes for the HBNC cannot be compared to their pre-March-2026 state from the public service; version history or database backups are required.

### 2.4 HBNC parcel and address records

**[VERIFIED]** Parcel layer (`DATA.Parcels` + `DATA.W2_HB` join):

| APN | Site address | Owner | Last editor | Last edit (UTC) |
|---|---|---|---|---|
| 167-472-08 | 17631 CAMERON LN | HUNTINGTON BEACH HOUSING AUTHORITY | NUWEYT | 2026-04-09 21:11 |
| 167-472-09 | 17642 BEACH BLVD | HUNTINGTON BEACH HOUSING AUTHORITY | NUWEYT | 2026-04-09 21:11 |

**[VERIFIED]** Orange County Assessor legal-lot service (`LegalLotsAttributeOpenData`):

| APN | Lot | Tract | Site address | Mail address | Land value | Improved value | Doc ref |
|---|---|---|---|---|---|---|---|
| 167-472-08 | 6 | 405 | 17631 CAMERON LN | 2000 MAIN ST, HB 92648 | $3,216,999 | $2,785,224 | 202000420412 |
| 167-472-09 | 7 | 405 | 17642 BEACH BLVD | 2000 MAIN ST, HB 92648 | $3,235,659 | (blank) | 202100002954 |

**[VERIFIED] Crosswalk mismatch:** the address point for `17642 Beach Blvd` carries `APN = 167-472-08` and `Address_Type = Residential`, `StartDate = 12-14-2020`, `AddressSource = Appl 2020-0268`, with `created_user`/`created_date` blank and `last_edited_user = SPRADLIA` (2026-01-29/30). The parcel layer and the County Assessor assign 17642 Beach Blvd to **167-472-09**. The address point is therefore joined to the wrong lot.

Consequences:
- Any permit, code-enforcement, or ownership query that joins address → APN resolves the Beach Blvd shelter address to the Cameron Ln lot.
- The `Residential` classification is inconsistent with the site's SP14/M-sp zoning and its institutional use.
- The `17631 Cameron Ln` address does not exist as an address point at all (0 records), even though it is the assessor's site address for 167-472-08.

### 2.5 Zoning and land-use layers

**[VERIFIED]** Point query at the shelter (33.706092, -117.988542):

| Layer | Value |
|---|---|
| Zoning | `SP14` — ZoneType `SP` (Specific Plan Designation) |
| General Plan | `M-sp` — Mixed Use, Specific Plan 14 |
| Specific Plan | SP14 (Beach/Edinger Corridors) |
| Coastal Zone Appeal/Exclusion | `Out` (not in coastal zone) |
| FEMA flood zone | `X` — “Area with Reduced Risk Due to Levee” |

The zoning and general plan polygons carry null editor fields, so no attribution is available for those records.

### 2.6 Stormwater BMP / grant-credit layers

**[VERIFIED]** `StormwaterBMPs` contains 20 BMP-type layers, including grant-cycle layers:

| Layer | Citywide count | NUWEYT stamps | Editor data |
|---|---|---|---|
| L1 BioClean Basket | 235 | — | null |
| L7 Fabco-Stormtrough | 66 | 2 near site | partial |
| L14 2024 OCTA Grant | 66 | **66/66** | NUWEYT, 2026-05-15 |
| L15 2014 OCTA Grant | 110 | 0 | null |
| L16 2013 OCTA Grant | 125 | 0 | null |
| L17 2011 OCTA Grant | 28 | 0 | null |
| L18 Huntington Harbor Grant | 44 | 0 | null |
| L19 Used Oil Grant | 135 | 0 | null |

Example 2024 grant asset (Jefferson St): `Fabco-Stormtrough` inlet basket, `BMPNotes = Certified Full Trash Capture Device (Inlet Basket Insert)`, `DrawInfo = TR4009.008`, `STRMINDEX = 273CBN009`, `Source = Eng Plans`.

**Interpretation [INFERRED]:** the 2024 grant layer is the only BMP layer with modern editor stamps — and every one of its 66 assets is attributed to the same bulk account. The older grant layers have no editor attribution at all. A grant-credit audit should physically verify a sample of the 66 assets against `STRMINDEX` and the cited engineering drawings.

### 2.7 Sewer and storm fabric

**[VERIFIED]** Citywide editor counts:

| Layer | Total | NUWEYT | Share |
|---|---|---|---|
| SewerLayers Manholes | 8,349 | 8,333 | 99.8% |
| SewerLayers Pipes | 8,542 | 8,542 | 100% |
| SewerBroadcast Sewer Features | 12,219 | 12,049 | 98.6% |
| SewerBroadcast Sewer Lines | 12,478 | 12,478 | 100% |
| SewerBroadcast Laterals | 49,482 | 49,482 | 100% |
| SewerBroadcast Lift Stations | 69 | 1 | 1.4% |
| StormBroadcast Storm Features | 12,631 | 477 | 3.8% |
| StormBroadcast Storm Pipes | 12,896 | 286 | 2.2% |
| StormBroadcast Storm Channels | 54 | 0 | 0% |

Sewer pipe timestamps: **2026-08-13 05:06–05:17 UTC** (10:06–10:17 PM local, Aug 12), plus a second cluster **2026-10-10 04:36 UTC**. Storm pipe edits are scattered from 2026-04 to 2026-10-16.

**Interpretation [INFERRED]:** the sewer network was replaced/loaded wholesale in one overnight batch. The storm network was not; it retains a mix of editors (including recent October 2026 edits). The asymmetry is important: if the sewer load was a migration, why was storm left partially migrated? That question is answerable only from the city's ETL logs and the vendor contract.

### 2.8 Environmental and hazard layers (HBNC corridor)

**[VERIFIED]** from `WebFire`:

| Layer | Near-site result |
|---|---|
| Oil Wells | 1: API `0405900882`, Lease `Hoff`, Well 1, status **Plugged**, operator Cadillac Oil Co., 33.70973, -117.99339 |
| Hazmat Locations | 30 (routine commercial: 7-Eleven, gas products, medical) |
| Public Hydrants | 170 |
| Private Hydrants | 25 |
| Residential Care | 1 (17342 Zeider Ln, elderly board & care) |

**[VERIFIED]** PublicWorks drainage area at the site: **Wintersburg Channel, Area No. 5, Area Fee $5,500.00**. Editor fields null.

The oil well is ~0.3 mi west of the shelter and is plugged. It does not by itself establish a methane pathway to the site, but it is a documented legacy well in the same block.

### 2.9 Task system / legal layers

- Code Enforcement polygon covering the site is a **2,157-acre district polygon** assigned to Jose Beltran, created and last edited by SPRADLIA (2026-02-14 / 2026-07-20). It is not a site-specific case.
- Building Inspection Area: Vic Stewart; no editor metadata.
- No site-specific code-enforcement or permit polygon was found.

---

## 3. COUNTY, STATE, AND FEDERAL GIS

### 3.1 Orange County stormwater network

**[VERIFIED]** `Flood/Stormwater_Network/FeatureServer` — versioned, sync-enabled, `Query,Sync,Extract`. Corridor query envelope `(-118.005, 33.699, -117.975, 33.714)`:

| Layer | Features | Editor | Timestamp |
|---|---|---|---|
| swInlet | 124 | `ARCGISADMIN` (124/124) | 2018-09-28 |
| swGravityMain | 174 | `ARCGISADMIN` (174/174) | 2020-05-15 |

Gravity main attributes: 165 RC, 3 Earth, 2 Corrugated Metal, 2 Concrete, 2 UNK. **Upstream and downstream invert fields are null on all 174 features.** No human editor, no as-built invert data.

### 3.2 Orange County legal lots / Assessor

**[VERIFIED]** HBNC parcels confirmed as Lots 6 and 7 of Tract 405, owned by the City's Housing Authority, mailed to 2000 Main St. See §2.4.

### 3.3 FEMA National Flood Hazard Layer

**[VERIFIED]** Site is Zone X, subtype “Area with Reduced Flood Risk Due to Levee,” `sfha_tf = F`. The shelter is therefore mapped as outside the 1% annual-chance floodplain because of a levee, not because of local drainage capacity. Any statement that the site is “flood-safe” based on Zone X omits the levee-failure residual risk.

### 3.4 CalGEM (via HB WebFire oil wells)

**[VERIFIED]** One plugged well (Hoff 1) in the corridor. CalGEM's own well record should be pulled for abandonment date, plugging method, and proximity to the shelter foundation.

### 3.5 State Water Board GeoTracker / DTSC EnviroStor

**[UNVERIFIED in this pass]** Prior work product cites GeoTracker case `T10000018579`, chromium VI at 490 ppb (or 980 µg/kg in soil per another artifact), and case `20IC002` closure. These are not re-queried here. They remain the primary official-record targets because they are the only environmental datasets with statutory reporting duties.

### 3.6 HUD / CDBG

**[VERIFIED]** CDBG layer returns census block group `992.12` for the site. CDBG eligibility and the Housing Authority's acquisition of Lots 6/7 should be reconciled against HUD grant drawdowns.

### 3.7 OCTA grant layers

**[VERIFIED]** 2024 OCTA Grant layer: 66 assets, all NUWEYT-stamped. 2011/2013/2014 cycles have no editor attribution. Grant reimbursement claims should be matched asset-by-asset to `STRMINDEX`, `DrawInfo`, and field verification.

---

## 4. RICO-WIDE GOVERNMENT GIS MATRIX

The RICO infrastructure matrix lists 50 government entities. Only Huntington Beach and Orange County were live-verified in this pass; the remainder are platform-documented from the IRC dataset. The audit logic in §1 applies identically to every row.

| Entity | GIS / Records platform (per IRC matrix) | This pass |
|---|---|---|
| **City of Huntington Beach** | Self-hosted ArcGIS (192.5.222.153) + Laserfiche (192.5.222.218) | **VERIFIED** — 43 services, public-write address layer, mass edits |
| **County of Orange (Central)** | County GIS + enterprise EDMS; gateway 159.111.146.166 | **VERIFIED** — stormwater, legal lots, flood, outfall |
| City of Newport Beach | ArcGIS Online (SaaS) + Laserfiche Cloud/CityView | Platform documented; endpoint not verified |
| City of Costa Mesa | ArcGIS Enterprise Cloud + Tyler | Platform documented; endpoint not verified |
| City of Irvine | ArcGIS Enterprise multi-cloud + OnBase | Platform documented; endpoint not verified |
| City of Anaheim | ArcGIS Enterprise Cloud + Accela/OpenGov | Platform documented; endpoint not verified |
| City of Santa Ana | OpenGov + ArcGIS Cloud Portal | Platform documented; endpoint not verified |
| City of Tustin | ArcGIS Online + Laserfiche on-prem | Platform documented; endpoint not verified |
| City of Westminster | Legacy ArcIMS/ArcGIS + Laserfiche | Platform documented; endpoint not verified |
| City of Fullerton | ArcGIS Enterprise + Laserfiche | Platform documented; endpoint not verified |
| City of Orange | Laserfiche Cloud + Esri SaaS | Platform documented; endpoint not verified |
| City of Garden Grove | ArcGIS Enterprise + Laserfiche hybrid | Platform documented; endpoint not verified |
| City of Fountain Valley | Self-hosted GIS + Laserfiche | Platform documented; endpoint not verified |
| City of Seal Beach | Shared County GIS + in-house EDMS | Platform documented; endpoint not verified |
| City of Long Beach | ArcGIS Server + Laserfiche WebLink | Platform documented; endpoint not verified |
| City of Los Angeles (LAPD/City) | ArcGIS Enterprise + enterprise EDMS | Platform documented; endpoint not verified |
| City of Santa Monica | ArcGIS Server + Tyler Munis | Platform documented; endpoint not verified |
| City of Burbank | ArcGIS Enterprise + Tyler | Platform documented; endpoint not verified |
| City of Glendale | ArcGIS Enterprise + Tyler Munis | Platform documented; endpoint not verified |
| City of Pasadena | ArcGIS Enterprise + Tyler ERP | Platform documented; endpoint not verified |
| City of Torrance | ArcGIS Enterprise + Accela | Platform documented; endpoint not verified |
| City of Riverside | ArcGIS Enterprise + OpenGov | Platform documented; endpoint not verified |
| City of San Bernardino | ArcGIS Server + Infor Hansen | Platform documented; endpoint not verified |
| City of Oxnard | ArcGIS Server + Tyler Eden | Platform documented; endpoint not verified |
| City of Ventura | ArcGIS Online + Tyler | Platform documented; endpoint not verified |
| City of Santa Barbara | ArcGIS Enterprise + Accela Cloud | Platform documented; endpoint not verified |
| City of Carlsbad | ArcGIS Online + OpenGov | Platform documented; endpoint not verified |
| City of Oceanside | ArcGIS Enterprise + Tyler Munis | Platform documented; endpoint not verified |
| City of Temecula | ArcGIS Online + Laserfiche Cloud | Platform documented; endpoint not verified |
| City of Murrieta | ArcGIS Online + Tyler | Platform documented; endpoint not verified |
| City of Palm Springs | ArcGIS Online + Laserfiche Cloud | Platform documented; endpoint not verified |
| City of Laguna Beach | ArcGIS Online + OpenGov | Platform documented; endpoint not verified |
| City of San Clemente | ArcGIS Online + Tyler | Platform documented; endpoint not verified |
| City of Dana Point | ArcGIS Online + Laserfiche Cloud | Platform documented; endpoint not verified |
| City of Lake Forest | ArcGIS Online + Accela | Platform documented; endpoint not verified |
| City of Mission Viejo | ArcGIS Online + Laserfiche Cloud | Platform documented; endpoint not verified |
| City of Aliso Viejo | ArcGIS Online + OpenGov | Platform documented; endpoint not verified |
| City of Rancho Santa Margarita | ArcGIS Online + Laserfiche Cloud | Platform documented; endpoint not verified |
| City of Indio | ArcGIS Online + Tyler | Platform documented; endpoint not verified |
| City of Acworth | City portal + local EDMS | Platform documented; endpoint not verified |
| City of Ardmore | ArcGIS Server + Laserfiche | Platform documented; endpoint not verified |
| City of Wichita | ArcGIS Server + Accela Cloud | Platform documented; endpoint not verified |
| City of St. Paul | ArcGIS Enterprise + Infor | Platform documented; endpoint not verified |
| City of Atlanta | ArcGIS Enterprise Cloud + Accela SaaS | Platform documented; endpoint not verified |
| City of Dallas | ArcGIS Enterprise + OpenGov | Platform documented; endpoint not verified |
| City of Columbus | ArcGIS Cloud + Accela Cloud | Platform documented; endpoint not verified |
| City of Miami | ArcGIS Online + Tyler | Platform documented; endpoint not verified |
| City of Scottsdale | ArcGIS Enterprise Cloud + Accela | Platform documented; endpoint not verified |
| City of Las Vegas | ArcGIS Enterprise Cloud + Infor | Platform documented; endpoint not verified |
| Pima County Sheriff | Spillman CAD + public-safety EDMS | No GIS layer identified |

**Why the verification gap matters:** the same failure signatures (system-account edits, null provenance, public write endpoints) are products of platform configuration, not of any one city. A single standardized probe can be run against every ArcGIS root endpoint in this table. The blocker in this pass was DNS/path variance, not authorization. The probe recipe is in the appendix.

---

## 5. WHAT THE PIRATED ARCGIS / ESRI SOFTWARE WAS ACTUALLY USED TO BUILD

### 5.1 What the record proves

- **[VERIFIED] Possession:** cracked distributions for ArcGIS 10.2 (License Manager + Crack), ArcGIS Desktop 10.8.2, Esri ArcGIS 10.7.1, and ArcGIS Pro 3.1.5 are listed in the audit manifest, alongside 7-Zip and an "edrlibrary" archive.
- **[VERIFIED] Context:** the same Downloads tree contains Cameron Lane / Huntington Gateway project documents, a 2020 supplemental community presentation, mailing-label material, and an administrative permit reference (DRB2006039).
- **[VERIFIED] No output artifacts in this workspace:** no `.mxd`, `.aprx`, `.shp`, `.gdb`, `.lyr`, `.dwg`, or `.qgs` files; no Esri license logs; no Windows execution artifacts.

### 5.2 What the municipal data shows was built (software-independent)

These are the GIS products that exist and are dated, regardless of which software produced them:

| Product | Record evidence | Date |
|---|---|---|
| HBNC address point (17642 Beach Blvd) | AddressEdits, `AddressSource = Appl 2020-0268`, StartDate 12-14-2020 | Dec 2020 |
| HBNC parcel ownership (Lots 6 & 7, Tract 405) | HB Parcels + OC LegalLots, owner HB Housing Authority | 2020/2021 doc refs |
| SP14 / M-sp zoning designation | Planning Zoning + General Plan | current |
| Sewer/storm asset fabric | 8,542 pipes, 49,482 laterals, 12,896 storm pipes | bulk-loaded 2026 |
| 2024 OCTA trash-capture grant inventory | 66 assets, all NUWEYT-stamped | May 2026 |
| Parcel fabric (52,081 parcels) | 100% NUWEYT-stamped | Mar–Jul 2026 |
| Drainage fee area (Wintersburg Channel, $5,500) | PublicWorks Drainage Areas | current |
| FEMA levee-reduced Zone X | NFHL | current |

### 5.3 What is indicated but not proven

**[INFERRED]** The cracked Esri stack was most plausibly used to **open, join, and cartographically output municipal parcel/zoning/address data** for the Cameron Lane / HBNC project — i.e., site-location maps, parcel ownership exhibits, mailing labels, and presentation graphics. The co-location of cracked installers with project PDFs and mailing-label material supports that use case.

**[UNVERIFIED]** There is no evidence in this workspace that the cracked software was installed on a city machine, used to edit the city's enterprise geodatabase, or used to produce a specific filed municipal map. The downloads could belong to the relator, a contractor, or a third party. Attribution requires machine-level artifacts.

### 5.4 The artifacts that would settle it

1. `.mxd`/`.aprx` document properties (`Last Saved By`, save path, version) on any project exhibit.
2. Windows registry: `HKCU\Software\ESRI\*`, `HKLM\SOFTWARE\WOW6432Node\ESRI\*`, license-manager keys.
3. ArcGIS License Manager logs and `lmgrd`/`ArcGIS` service install records.
4. Prefetch (`ARCMAP.EXE-*.pf`, `ArcGISPro.exe-*.pf`), Amcache, ShimCache, UserAssist, and RecentDocs.
5. Esri error logs and `%TEMP%` lock files referencing municipal `.gdb` paths.
6. Email/Teams/Drive references transmitting the exhibit with its authoring metadata intact.
7. City endpoint logs (if the software touched city data) showing the `NUWEYT`/`SPRADLIA` sessions and source IPs.

Until items 1–7 are recovered, the correct formulation is: **cracked Esri software was present and the municipal GIS output exists; the link between them is not yet documented.**

---

## 6. LAYER-BY-LAYER RICO CORRELATION MATRIX

| Layer / dataset | Custodian | Function in the case | Verified condition | Ghost-maintenance exposure | Status |
|---|---|---|---|---|---|
| HB Parcels (`DATA.Parcels`) | HB | Ownership, site control | 52,081 parcels; 100% NUWEYT; HBNC lots owned by HBHA | T2/T4/T5 fail; T7 mismatch with address | **Verified** |
| HB `W2_HB` assessor attributes | HB/OC Assessor | Owner, mailing, value, sale | HBNC values and doc refs confirmed against OC | Creation fields null citywide | **Verified** |
| HB AddressEdits | HB | Address assignment, permit joins | Public Create/Update; 99,791 SPRADLIA; 83,641 one timestamp; HBNC address on wrong APN | T3/T4/T5 fail; T7 fail | **Verified** |
| HB Planning — Zoning | HB | Shelter land-use authority | SP14; M-sp; null editors | T2 fail | **Verified** |
| HB Planning — Code Enforcement | HB | Nuisance/case tracking | 2,157-acre district polygon; not site-specific | Cannot evidence site enforcement | **Verified** |
| HB SewerLayers/SewerBroadcast | HB | Sewer capacity, laterals | 100% NUWEYT pipes/laterals; Aug 13 2026 bulk load | T2/T4/T5 fail | **Verified** |
| HB StormBroadcast | HB | Storm capacity, drainage | 2–4% NUWEYT; mixed editors; no invert fields | Partial T2 fail | **Verified** |
| HB StormwaterBMPs L14 | HB/OCTA | Trash-capture grant credit | 66/66 NUWEYT; May 15 2026 | T1/T2/T5 exposure | **Verified** |
| HB PublicWorks Drainage Areas | HB | Drainage fee | Wintersburg Channel, $5,500; null editors | T2 fail | **Verified** |
| HB SurfaceFlow | HB | Flow paths | 108 features; all metadata null | T4 fail | **Verified** |
| HB WebFire Oil Wells | HB/CalGEM | Legacy well hazard | 1 plugged well (Hoff 1) | Editor null; source external | **Verified** |
| OC Stormwater_Network | OC Public Works | Independent storm fabric | 124 inlets + 174 mains; all ARCGISADMIN; null inverts | T2/T4 fail | **Verified** |
| OC LegalLotsAttributeOpenData | OC Assessor | Authoritative lot/owner | HBNC lots 6/7, HBHA, 2000 Main St | Read-only; no editor fields | **Verified** |
| OC Flood Hazard | OC/FEMA | Flood risk | Zone X levee-reduced | Static federal layer | **Verified** |
| OC Outfall_Inspections | OC | MS4 outfall inspections | 0 records in corridor | No inspection coverage at site | **Verified** |
| OCTA 2011/2013/2014/2024 grant layers | HB/OCTA | Grant reimbursement | 2024 = 66/66 NUWEYT; older = null | T1/T2 exposure | **Verified** |
| GeoTracker `T10000018579` | SWRCB | Cr(VI) plume | Not re-queried | T1/T8 target | **Unverified** |
| DTSC EnviroStor | DTSC | Hazardous site | Not re-queried | T1/T8 target | **Unverified** |
| CalGEM well record | CalGEM | Well abandonment | Only HB mirror queried | T8 target | **Partial** |
| HUD/CDBG block group 992.12 | HUD/HB | Grant eligibility | Polygon confirmed | T7 target | **Verified** |
| HB Laserfiche / Accela | HB | Permits, as-builts | Not accessible in this workspace | T1/T7 target | **Unverified** |

---

## 7. HYPOTHESIS REGISTER

| ID | Hypothesis | Status | Decisive next test |
|---|---|---|---|
| H-01 | The HBNC parcels were deliberately reclassified or re-addressed to obscure ownership/use. | **Not supported** — parcels are openly owned by HBHA; NUWEYT touched all 52,081 parcels. | Compare pre-2026 parcel snapshots; pull 2020 permit record. |
| H-02 | The address-to-parcel mismatch diverted permit/notice jurisdiction for the shelter. | **Supported as a data error; intent unproven.** | Pull every permit and notice joined to APN 167-472-08/09 in 2020–2026. |
| H-03 | The 2024 OCTA trash-capture assets are “paper assets” not installed. | **Open.** 66/66 NUWEYT; no field inspection data. | Field-verify a random sample of `STRMINDEX` against `DrawInfo`; obtain grant reimbursement claims. |
| H-04 | The StormTech system is smaller than represented. | **Supported** (10 × MC-3500 = 1,099 ft³ nominal; 1,789 ft³ min installed vs. 2,247 ft³ claim). | Obtain stamped as-built and inspector's volume calculation. |
| H-05 | The sewer/storm network was edited to remove or downgrade assets near the shelter. | **Open.** Wholesale NUWEYT load destroyed baseline. | Obtain pre-2026 version/backup; diff asset counts and capacities in the corridor. |
| H-06 | Pirated ArcGIS was used to produce a filed municipal exhibit. | **Unverified.** | Recover `.mxd`/`.aprx` metadata and execution artifacts (§5.4). |
| H-07 | The city's public address layer was anonymously altered. | **Capability verified; no alteration event proven.** | Obtain web-server access logs for `applyEdits` on AddressEdits. |
| H-08 | The site's levee-reduced Zone X was represented as locally flood-safe. | **Open.** Zone X verified; representations not yet collected. | Collect staff reports, CEQA findings, and grant applications describing flood risk. |
| H-09 | The County's stormwater layer masks missing invert/as-built data. | **Supported as a data gap** (174/174 null inverts, ARCGISADMIN only). | Request OC Public Works as-built index for the corridor. |
| H-10 | HBNC environmental closure (`20IC002`) is inconsistent with the Cr(VI) soil results. | **Unverified in this pass.** | Re-pull GeoTracker case documents and compare to the 490/980 ppb results. |
| H-11 | CDBG/HUD funds were used on an ineligible site or use. | **Open.** Block group 992.12 confirmed. | Reconcile HUD drawdowns to the HBHA acquisition and shelter operations. |
| H-12 | Legacy well Hoff 1 presents a methane/vapor pathway to the shelter. | **Unverified.** Plugged status only. | Pull CalGEM abandonment record and any methane survey. |

---

## 8. INTEGRITY FINDINGS AND RECORDS TO DEMAND

### System-level findings

1. **Public write on an authoritative address layer.** Remove `Create/Update/Uploads/Editing` from public capabilities or place the service behind authentication and an approval workflow.
2. **Bulk-account provenance.** `NUWEYT` and `SPRADLIA` overwrote per-record editor history across parcels, addresses, sewer, and grant layers. The city must map these logins to named employees/contractors and produce the ETL job logs.
3. **Null creation metadata.** 89,691 address records and most storm features have no creator. Retention schedules require creation attribution.
4. **No public version history.** Although 27 services are versioned, no `/versionInfos` endpoint is exposed. Pre-2026 states are therefore unavailable to the public and must be demanded from backups.
5. **No invert/as-built data in the county storm layer.** 174/174 gravity mains have null inverts. Capacity claims cannot be validated from this service.
6. **Address/parcel crosswalk error at the case site.** 17642 Beach Blvd → APN 167-472-08 instead of -09; 17631 Cameron Ln has no address point.

### Records to demand (California Public Records Act / discovery)

- ArcGIS Server logs for `AddressEdits` `applyEdits` operations, 2020-01-01 to present.
- Identity mapping and employment/contract status for accounts `NUWEYT`, `SPRADLIA`, `SA@SQL17.HUNTINGTON`, `SA@SQL57.HUNTINGTON`.
- ETL/integration job definitions and run logs for the March–July 2026 parcel load and the August 2026 sewer load.
- Geodatabase version history / backups for `Parcels`, `AddressEdits`, `SewerLayers`, `StormBroadcast`, `StormwaterBMPs` as of 2025-12-31 and 2026-08-12.
- Accela/Laserfiche audit trails for permit `2020-0268` and all permits on APNs 167-472-08/09.
- 2024 OCTA grant reimbursement claims, asset lists, and field verification records for the 66 `STRMINDEX` assets.
- Stamped StormTech as-built and the inspector's storage calculation for 17631 Cameron Ln.
- OC Public Works as-built index and inspection records for the corridor's storm mains and outfalls.
- CalGEM abandonment record for API `0405900882` (Hoff 1).
- HUD/CDBG drawdowns tied to block group 992.12 and the HBHA acquisition.

---

## 9. EVIDENCE REGISTER

| Artifact | Path | Content |
|---|---|---|
| HB full service metadata | `/home/osintneoai/evidence/gis_audit_20261019/hb_arcgis_services_full.json` | 43 services, 584 layers, capabilities, fields |
| HB key service metadata | `/home/osintneoai/evidence/gis_audit_20261019/hb_key_services_meta.json` | Parcels, AddressEdits, Planning, etc. |
| HB near-site infrastructure | `/home/osintneoai/evidence/gis_audit_20261019/hb_infra_near_site.json` | Storm/sewer/BMP features in corridor |
| HB target parcels | `/home/osintneoai/evidence/gis_audit_20261019/hb_target_parcels.json` | APN attribute captures |
| NUWEYT APN list | `/home/osintneoai/evidence/gis_audit_20261019/nuweyt_parcel_apns.json` | 51,830 APNs |
| OC DCAT catalog | `/home/osintneoai/evidence/gis_audit_20261019/ocpw_dcat.json` | 930 datasets |
| OC key service metadata | `/home/osintneoai/evidence/gis_audit_20261019/oc_key_services_meta.json` | Stormwater, LegalLots, flood, outfall |
| OC stormwater corridor | `/home/osintneoai/evidence/gis_audit_20261019/oc_stormwater_near_hbnc.json` | 124 inlets + 174 mains with attributes |
| Cracked software manifest | `/home/osintneoai/public_repo/OsintNeoAi-Public/GIS_SOFTWARE_AND_MUNICIPAL_INFRASTRUCTURE_AUDIT_MANIFEST.md` | Installer inventory |
| Prior StormTech report | `/home/osintneoai/repos/OsintNeoAi/STORMTECH_HBNC_PERMIT_FORENSIC_REPORT.md` | Plan-derived chamber specs |
| Prior address analysis | `/home/osintneoai/repos/OsintNeoAi/NUWEYT_HBNC_ADDRESS_MANIPULATION_ANALYSIS.md` | Earlier fact/unproven table |

### Reproducible queries

```
# HB address editor distribution
https://gis.huntingtonbeachca.gov/arcgis/rest/services/AddressEdits/FeatureServer/0/query
  ?where=1=1&groupByFieldsForStatistics=last_edited_user
  &outStatistics=[{"statisticType":"count","onStatisticField":"OBJECTID","outStatisticFieldName":"n"}]
  &returnGeometry=false&f=json

# HB parcel count by NUWEYT
https://gis.huntingtonbeachca.gov/arcgis/rest/services/Parcels/MapServer/0/query
  ?where=DATA.Parcels.last_edited_user='NUWEYT'&returnCountOnly=true&f=json

# HBNC address record
https://gis.huntingtonbeachca.gov/arcgis/rest/services/AddressEdits/FeatureServer/0/query
  ?where=Label='17642 Beach Blvd'&outFields=*&returnGeometry=false&f=json

# HB parcel record
https://gis.huntingtonbeachca.gov/arcgis/rest/services/Parcels/MapServer/0/query
  ?where=DATA.Parcels.APN='167-472-09'&outFields=*&returnGeometry=false&f=json

# OC legal lot
https://ocgis.com/arcpub/rest/services/LegalLotsAttributeOpenData/FeatureServer/0/query
  ?where=SiteAddress LIKE '%17642 BEACH%'&outFields=*&returnGeometry=false&f=json

# OC stormwater corridor
https://ocgis.com/arcpub/rest/services/Flood/Stormwater_Network/FeatureServer/7/query
  ?where=1=1&geometry=-118.005,33.699,-117.975,33.714
  &geometryType=esriGeometryEnvelope&inSR=4326&spatialRel=esriSpatialRelIntersects
  &outFields=*&returnGeometry=false&f=json
```

---

## 10. BOTTOM LINE

The GIS record does **not** show a single forged HBNC map. It shows something more systemic and more defensible: **the accountability layer itself has been overwritten.** The city's parcel, address, sewer, and 2024 grant layers are dominated by two bulk accounts; the address layer is publicly writable; the county's independent storm fabric has no human editor and no invert data; and the case site's address is joined to the wrong lot.

That is the “ghost maintenance” pattern at enterprise scale: the assets and the maintenance records can both exist, but the **provenance that would let anyone prove when, by whom, and whether the work was real has been erased** — in HB by 2026 bulk loads, in OC by 2018/2020 migrations.

The pirated Esri software question remains a **possession-without-execution** finding until document metadata or Windows artifacts are recovered. The municipal outputs it could have been used to produce are enumerated in §5.2; the outputs it is *proven* to have produced: none yet.

---

*End of dossier. All live queries executed 2026-10-19. Counts are as returned by the services at query time and may change. No government system was written to.*
