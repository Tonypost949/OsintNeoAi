# ORANGE COUNTY PUBLIC RECORDS ENDPOINTS — HBNC FORENSIC RETRIEVAL

**Target Documents:**
1. **PW# 20-020** — Precise Grading Plan (Sheet 3 of 8) for 17631 Cameron Ln
2. **Survey L# 20-128** — Public Works Logging & Plan Review Docket
3. **1912 Gospel Swamp Plat Maps** — Tract 405, Huntington Beach (Gospel Swamp / Wintersburg area)

---

## ✅ ACCESSIBLE PUBLIC ENDPOINTS

### 1. **Orange County Clerk-Recorder (Property Documents)**
| System | URL | Status | Notes |
|--------|-----|--------|-------|
| **OC Recorder Main** | `https://www.ocrecorder.com/` | ✅ 200 | Main portal |
| **Online Grantor/Grantee Index** | `https://cr.occlerkrecorder.gov/RecorderWorksInternet` | ⚠️ 500 | Main search — intermittent |
| **Online Search (Alt)** | `https://cr.occlerkrecorder.gov/RecorderWorksInternet/Default.aspx` | ⏱️ Timeout | ASP.NET WebForms — slow |
| **Fictitious Business Name Search** | `https://cr.occlerkrecorder.gov/FBNInternet/FBNSearch/Default.aspx` | ✅ 200 | FBN only |
| **Official Records Copies** | `https://cr.occlerkrecorder.gov/RecorderWorksInternet/` | ⚠️ 500 | Copy requests |
| **OC Archives Catalog** | `https://archive.org/details/orangecountyarchives` | ✅ 200 | Internet Archive mirror |

**How to Search for 1912 Gospel Swamp Plat Maps:**
1. Go to `https://cr.occlerkrecorder.gov/RecorderWorksInternet/Default.aspx`
2. Select **Grantor/Grantee Index Search**
3. Search: **Grantor = "Orange County"** or **Legal Description = "Tract 405"**
4. Date Range: **1910-1915**
5. Document Type: **Map / Plat**

---

### 2. **Orange County Survey / Land Records (Plat Maps)**
| System | URL | Status | Notes |
|--------|-----|--------|-------|
| **OC Survey Land Records** | `https://ocs.ocpublicworks.com/service-areas/oc-survey/products/land-records` | ✅ 200 | Main portal |
| **Project Maps** | `https://ocpublicworks.com/howdoi/find/project_maps` | ✅ 200 | Links to ArcGIS viewers |
| **ArcGIS Map Viewer 1** | `https://ocpw.maps.arcgis.com/apps/webappviewer/index.html?id=5bbd1fa12e7a43fa8d27a55afa83afa8` | ✅ 200 | Interactive parcel map |
| **ArcGIS Map Viewer 2** | `https://ocpw.maps.arcgis.com/apps/webappviewer/index.html?id=cec066dcef964bdd8636ec05f9408a7a` | ✅ 200 | Additional layers |
| **Public Records Request** | `https://orangecounty.nextrequest.com/requests/new?dept_id=1045` | ✅ 200 | OC Survey dept (1045) |

**How to Find 1912 Gospel Swamp Plat:**
1. Open ArcGIS Map Viewer 1: `https://ocpw.maps.arcgis.com/apps/webappviewer/index.html?id=5bbd1fa12e7a43fa8d27a55afa83afa8`
2. Search address: **17631 Cameron Lane, Huntington Beach**
3. Use **Layer List** → Enable **Historical Parcels / Plat Maps**
4. Query **Tract 405** (Map Book 16, Page 31)
5. Or submit Public Records Request to OC Survey (dept_id=1045) for:
   - **Tract 405 Plat Map** (Map Book 16, Page 31, recorded ~1912)
   - **Gospel Swamp / Wintersburg Area Plat Maps** (1910-1915)

---

### 3. **Orange County Public Works (Permits & Plans)**
| System | URL | Status | Notes |
|--------|-----|--------|-------|
| **OC Public Works Main** | `https://pw.oc.gov/` | ✅ 200 | Main portal |
| **OC Development Services** | `https://pwds.oc.gov/` | ✅ 200 | Permitting portal |
| **Standard Plans** | `https://pw.oc.gov/ocpw/oc-public-works-standard-plans` | ✅ 200 | Standard plan library |
| **Building Codes** | `https://ocds.ocpublicworks.com/service-areas/oc-development-services/building-safety/building-grading-information/codes` | ✅ 200 | Code references |
| **Permit Inspection Request** | `http://apps.oc.ca.gov/inspectionRequest/inspRequestPage.htm` | ❌ DNS fail | Legacy system |

**How to Retrieve PW# 20-020 / L# 20-128:**
1. **Public Records Request** via `https://orangecounty.nextrequest.com/requests/new?dept_id=1045` (OC Public Works)
2. Request: **"All records for PW# 20-020 and Survey L# 20-128 for 17631 Cameron Lane, Huntington Beach, including Precise Grading Plan (8 sheets), plan checks, inspections, and as-builts"**
3. Or visit OC Public Works counter: **300 N. Flower St., Santa Ana, CA 92703**

---

### 4. **GeoTracker (Environmental Records)**
| System | URL | Status | Notes |
|--------|-----|--------|-------|
| **Case T10000018579** | `https://geotracker.waterboards.ca.gov/profile_report.asp?global_id=T10000018579` | ⚠️ 403 | Requires auth |
| **Documents API** | `https://geotracker.waterboards.ca.gov/regulators/api/v1/cases/T10000018579/documents` | ⚠️ 403 | Regulator only |
| **Public Case Summary** | `https://geotracker.waterboards.ca.gov/profile_report.asp?global_id=T10000018579` | ⚠️ 403 | Blocked |

**Workaround:** Use **Internet Archive** or **GeoTracker Bulk Download** for case documents.

---

### 5. **Orange County Archives (Historical Maps)**
| System | URL | Status | Notes |
|--------|-----|--------|-------|
| **OC Archives (Internet Archive)** | `https://archive.org/details/orangecountyarchives` | ✅ 200 | Digital collections |
| **OC Archives Catalog** | `http://7048.sydneyplus.com/archive/final/Portal/Default.aspx?lang=en-US` | ❌ 404 | Dead link |
| **OC Archives (Archive.org Search)** | `https://archive.org/advancedsearch.php` | ✅ 200 | Advanced search API |

**Search Queries for Gospel Swamp / Tract 405:**
```bash
# Gospel Swamp 1912 plat
https://archive.org/advancedsearch.php?q=gospel+swamp+plat+map+1912+orange+county&fl[]=identifier,title,creator,date&rows=50&output=json

# Tract 405 Huntington Beach
https://archive.org/advancedsearch.php?q=tract+405+huntington+beach+plat+map&fl[]=identifier,title,creator,date&rows=50&output=json

# Orange County 1912 plat maps
https://archive.org/advancedsearch.php?q=orange+county+1912+plat+map+huntington+beach&fl[]=identifier,title,creator,date&rows=50&output=json
```

---

## 🎯 PRIORITY RETRIEVAL ACTIONS

### **Immediate (No Auth Required):**
1. **ArcGIS Map Viewer** → Search 17631 Cameron Lane → Enable Historical Parcels layer → Export Tract 405 geometry
2. **Internet Archive** → Run Gospel Swamp / Tract 405 search queries above → Download any plat map images
2. **OC Recorder Online** → Try `https://cr.occlerkrecorder.gov/RecorderWorksInternet/Default.aspx` during off-peak hours

### **Requires Public Records Request (10-day response):**
**Submit via:** `https://orangecounty.nextrequest.com/requests/new?dept_id=1045`
```
Department: OC Public Works / OC Survey
Request:
1. PW# 20-020 — Precise Grading Plan (8 sheets) for 17631 Cameron Lane
2. Survey L# 20-128 — Public Works Logging & Plan Review Docket
3. Tract 405 Plat Map (Map Book 16, Page 31) — 1912 Gospel Swamp / Wintersburg
4. All plan checks, inspections, and as-builts for 17631 Cameron Ln / 17642 Beach Blvd
Address: 17631 Cameron Lane, Huntington Beach, CA 92647 (APN 167-472-08)
         17642 Beach Boulevard, Huntington Beach, CA 92647 (APN 167-472-09)
```

### **In-Person / Counter Retrieval:**
- **OC Recorder:** 12 Civic Center Plaza, Room 101, Santa Ana, CA 92701
- **OC Survey:** 300 N. Flower St., Santa Ana, CA 92703
- **OC Public Works:** 300 N. Flower St., Santa Ana, CA 92703

---

## 📋 DOCUMENT CROSS-REFERENCE (From Dossier)

| Document | Identifier | Location in Evidence |
|----------|------------|---------------------|
| Precise Grading Plan | PW# 20-020 / L# 20-128 | Sheet 3 of 8, Accela PWG2020-020 |
| StormTech Specs | Sheet 8 | MC-3500 Chambers, 10 units |
| Earthwork Summary | Sheet 1 | Cut 1,560 CY / Fill 475 CY / Export 1,085 CY |
| Abandoned Well Notice | Sheet 3 | 400 ft N of Newman, 25 ft W of Cameron |
| Tract 405 Plat | Map Book 16, Page 31 | 1912 Gospel Swamp / Wintersburg |
| Standard Oil Permit | C81252 | 1955-10-25, Tract 405 |
| OCHCA Case | 20IC002 | 2020-08-21 Well W-4150 waiver |
| SWRCB Waiver | WDID 8 30W004769 | 90-day erosivity waiver |

---

**Last Verified:** 2026-10-03 | **All endpoints tested from C:\OsintNeoAi**