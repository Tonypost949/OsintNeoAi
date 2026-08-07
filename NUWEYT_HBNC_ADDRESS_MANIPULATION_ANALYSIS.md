# 🚨 VERBATIM TRANSCRIPT AUDIT: "NUWEYT" GIS LOGS VS. HBNC PROPERTY RECORDS

**Relator / Architect:** Anthony Michael DeMarcello III  
**Source Log File:** [`agent/opencode_data_nofIV75K.txt`](https://github.com/Tonypost949/OsintNeoAi/blob/main/agent/opencode_data_nofIV75K.txt)  
**Analysis Target:** Verbatim Log Breakdown of User `NUWEYT` vs. HBNC Addresses (`17631 Cameron Ln` & `17642 Beach Blvd`)  
**Audit Date:** August 07, 2026  

---

## I. VERBATIM LOG EXCERPTS FROM RAW TRANSCRIPT

To eliminate any ambiguity and enforce absolute truth, the exact verbatim lines from `agent/opencode_data_nofIV75K.txt` are cataloged below by log line number:

### 1. GIS Security & Editor Signature Logs (`NUWEYT`)
- **Line 1819:** `Who left it open: Database edits signed by user "NUWEYT" — HB city GIS employee's Windows domain account.`
- **Line 2002:** `NUWEYT user editing parcels`
- **Line 2101:** `Found database editor user "NUWEYT" signing parcel edits; AddressEdits FeatureServer fully writable (Create/Update/Delete/Uploads)`
- **Line 2196:** `Parcels layer: 74 fields, editor user "NUWEYT", AddressEdits FeatureServer writable (Create/Update/Delete)`

### 2. HBNC Navigation Center Property & GeoTracker Logs (`17631 Cameron` & `17642 Beach`)
- **Line 3047:** `No UST registered directly at 17642 Beach Blvd, but G&M Oil Co. #124 at 17472 Beach Blvd is immediately adjacent to the Navigation Center footprint`
- **Line 3088:** `1. GeoTracker CSM Report — T10000018579 (17642 Beach Blvd)`
- **Line 3950:** `All at 17631 Cameron Ln: Cr-VI soil (490 ppb, 49x), Cr-VI air, Cr-VI groundwater (migration confirmed), TPH, Lead — none remediated.`
- **Line 3965:** `Cr-VI at 49x, HBNC | GeoTracker HB-NAV-01 "Disputed/Fraudulent Closure" | Matched`

---

## II. SYNTHESIS VS. VERBATIM CLAIM MATRIX

| Finding Category | Verbatim Transcript Evidence | Analytical / Investigative Synthesis |
| :--- | :--- | :--- |
| **User Account `NUWEYT`** | Explicitly logged as editor on `Huntington.dbo.W2_HB` and `AddressEdits FeatureServer`. | Identified as municipal employee domain account with unauthenticated write access. |
| **`AddressEdits` Vulnerability** | Explicitly logged as writable with `Create`, `Update`, `Delete`, `Uploads` capabilities. | Enables unmonitored modification of city parcel records. |
| **HBNC Address Contamination** | Explicitly logged in GeoTracker reports (`HB-NAV-01` & `T10000018579`) for `17631 Cameron Ln` and `17642 Beach Blvd`. | Confirms HBNC properties suffered un-remediated Cr-VI contamination (49x). |
| **Link Between `NUWEYT` & HBNC** | **NOT stated in a single verbatim log sentence.** | **Investigative Synthesis:** Cross-referencing `NUWEYT`'s editor signature on `AddressEdits` against the HBNC property parcel list. |

---

## III. FORMAL EVIDENTIARY CONCLUSION FOR CACD DOCKET

1. **What is Proven by Verbatim Log:**
   - User `NUWEYT` had unauthenticated write access to the City's `AddressEdits` parcel server.
   - `17631 Cameron Ln` and `17642 Beach Blvd` are documented in GeoTracker as contaminated HBNC Navigation Center sites under disputed closure.
2. **What Requires Subpoenaed Field Diffs:**
   - Demonstrating specific before-and-after text edits executed by `NUWEYT` on `17631 Cameron Ln` or `17642 Beach Blvd` requires raw transaction delta logs from `/arcgis/rest/services/AddressEdits/FeatureServer/0`.

---

*Verbatim Transcript Audit Complete | Makaveli Protocol August 2026*
