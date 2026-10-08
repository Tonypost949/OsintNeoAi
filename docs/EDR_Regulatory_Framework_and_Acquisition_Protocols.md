# Regulatory Framework and Acquisition Protocols for Environmental Data Records (EDR)

## 1. Statutory Foundations & Mandatory EDR Acquisition Standards

Environmental Data Records (EDR) and historical municipal intelligence extractions operate under strict federal and state regulatory mandates to determine Phase I/II Environmental Site Assessment (ESA) liabilities, Superfund proximity, and title defect boundaries.

### A. ASTM E1527-21 Standard Practice for Environmental Site Assessments
- **0.5-Mile to 1.0-Mile Standard Search Radii:** Requires comprehensive evaluation of federal Superfund (CERCLA/NPL), state-equivalent sites (DTSC EnviroStor), leaking underground storage tanks (SWRCB GeoTracker LUST/SLIC), and historical industrial land use directories.
- **Historical Use Extraction:** Mandates searching Sanborn Fire Insurance Maps, City Directories, Historical Aerial Photography, and Building Department permits back to first developed use or 1937 (whichever is earlier).
- **Recognized Environmental Conditions (RECs):** Identification of controlled RECs (CRECs) and historical RECs (HRECs) that impact property valuation and chain of custody.

### B. California Carpenter-Presley-Tanner Hazardous Substance Account Act (HSAA)
- **Cal. Health & Safety Code § 25300 et seq.:** Governs state-level cost recovery, strict joint and several liability for hazardous substance releases, and mandatory disclosure covenants.
- **Cortese List (Cal. Gov. Code § 65962.5):** Mandatory public listing of contaminated sites, public water wells with hazardous levels of chemicals, and land use restrictions.

### C. CERCLA Superfund Liability & Innocent Landowner Defense
- **42 U.S.C. § 9601(35)(B):** Requires "All Appropriate Inquiries" (AAI) conducted prior to acquisition to claim Innocent Landowner, Contiguous Property Owner, or Bona Fide Prospective Purchaser (BFPP) status.
- **Suppression of Known EDR Hits:** Concealment of active SLIC/LUST or Hexavalent Chromium plume data during real estate transactions voids AAI protections and establishes intentional fraudulent concealment under Cal. Civ. Proc. Code § 473(d).

---

## 2. Technical Acquisition & Data Mining Protocols

```
┌────────────────────────────────────────────────────────────────────────┐
│                        RAW DATA SOURCES & PIPELINES                    │
├───────────────────────────────┬────────────────────────────────────────┤
│ 1. Federal/State REST APIs    │ DTSC EnviroStor, CalEPA GeoTracker     │
│ 2. EDR Master Radius Maps     │ Sanborn Maps, EDR City Directories     │
│ 3. Municipal Zoning Portals   │ OC Public Works, OCGIS Land Records    │
└───────────────┬───────────────┴────────────────────┬───────────────────┘
                │                                    │
                ▼                                    ▼
┌────────────────────────────────┐  ┌──────────────────────────────────┐
│   Zero-Trust Ingestion Engine  │  │ Spatial Query Geofence (0.5-Mi)  │
│  (dynamic_genesis_webhook.py)  │  │   (17631 Cameron Lane Anchor)    │
└───────────────┬────────────────┘  └────────────────┬─────────────────┘
                │                                    │
                └───────────────────┬────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                 BIGQUERY APPEND-ONLY LEDGER VAULT                     │
│        noble-beanbag-497411-m4.forensic_layers.genesis_ledger          │
└────────────────────────────────────────────────────────────────────────┘
```

### Protocol A: EDR Historical City Directory Assessment Workflow
1. **Target Geofence Definition:** Establish exact spatial parcel anchor (e.g., `17631 Cameron Lane, Huntington Beach, CA`, Lat: `33.7225° N`, Long: `117.9897° W`) with a mandatory 0.5-mile radial buffer.
2. **Directory Timeline Extraction:** OCR scan and parse municipal street directories in 5-year increments (1950–2025).
3. **Categorization & Risk Scoring:**
   - **High Risk:** Chemical Plating, Dry Cleaning, Solvent Recovery, Oilfield Sumps, Degreasing Depots.
   - **Medium Risk:** Automotive Repair, Fuel Stations, Historical Machine Shops.
   - **Low/Neutral:** Retail, Residential, Open Space.
4. **Automated Ledger Commit:** Hash raw payload (SHA-256) and write zero-value unmined block to BigQuery staging directory (`C:\OsintNeoAi\data\staging\`).

---

## 3. Evidence Locker Master Paths & System Integration

All acquisition workflows enforce strict chain-of-custody tracking across local directories and cloud backups:

- **Master Evidence Locker:** `C:\EVIDENCE_LOCKER_MASTER`
- **Google Drive Mirror:** `gdrive:Sharedall/EVIDENCE_LOCKER_MASTER`
- **Historical City Directory EDR Manifest:** `C:\EVIDENCE_LOCKER_MASTER\Historical_City_Directories_Cameron_Lane_1950_2025.txt`
- **2025 EDR Radius Map Manifest:** `C:\EVIDENCE_LOCKER_MASTER\2025_EDR_Radius_Map_Cameron_Lane.txt`
- **Eurofins Contaminant Hits Master CSV:** `C:\EVIDENCE_LOCKER_MASTER\Eurofins_Contaminant_Hits_Master.csv`
- **Huntington Beach Municipal URLs Index:** `C:\OsintNeoAi\data\hb_urls_master.txt`
- **BigQuery Sync Worker:** [bq_sync_worker.py](file:///C:/OsintNeoAi/scripts/bq_sync_worker.py)
- **City Directory Analyzer:** [city_directory_assessment.py](file:///C:/OsintNeoAi/scripts/city_directory_assessment.py)
- **Workspace UI Server:** `http://localhost:8080/workspace_v2.html`
