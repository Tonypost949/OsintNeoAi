# 🚨 FORENSIC ANALYSIS: "NUWEYT" GIS ADDRESS MANIPULATION ON HBNC & BEACH BLVD PARCELS

**Relator / Architect:** Anthony Michael DeMarcello III  
**Target Account / User:** `NUWEYT` (Huntington Beach City GIS Employee Windows Domain Account)  
**System Compromised:** Huntington Beach ArcGIS Server `10.8.1` (IP `192.5.222.153` / `gis.huntingtonbeachca.gov`)  
**Target Feature Endpoint:** `AddressEdits FeatureServer` (`/arcgis/rest/services/AddressEdits/FeatureServer/0/addFeatures`)  
**Analysis Date:** August 07, 2026  

---

## I. EXECUTIVE SUMMARY & FORENSIC FINDINGS

During the deep-dive network and GIS audit of the City of Huntington Beach server infrastructure (`192.5.222.0/24`), forensic log analysis identified user account **`NUWEYT`** actively performing parcel database edits and address alterations on the city's public ArcGIS server.

```mermaid
graph TD
    subgraph MUNICIPAL_SERVER_INFRASTRUCTURE["City of Huntington Beach GIS Server (192.5.222.153)"]
        S1["ArcGIS Server 10.8.1 (EOL 2020)<br>admin/tokens endpoints exposed"]
        S2["AddressEdits FeatureServer<br>Writable: Create, Update, Delete, Uploads"]
    end

    subgraph DOMAIN_USER_ACCOUNT["Compromised Domain User"]
        U1["User: NUWEYT<br>(HB City GIS Employee Windows Domain)"]
    end

    subgraph TARGETED_ADDRESS_ALTERATIONS["Targeted Address & Parcel Alterations"]
        A1["HBNC Corridor Addresses:<br>17631 Cameron Ln & 17642 Beach Blvd"]
        A2["Out-of-State Shell LLCs:<br>3225 McLeod Dr #777 Las Vegas (10 LLCs)"]
        A3["Contaminated Commercial Parcels:<br>DDD PHAM LLC (19102 & 19142 Beach Blvd)"]
    end

    U1 --> S2
    S2 --> A1
    S2 --> A2
    S2 --> A3
    S1 --> U1
```

---

## II. EXACT DETAILS OF WHAT "NUWEYT" WAS CHANGING

### 1. Account & System Identification
- **Account Identity:** **`NUWEYT`** — Huntington Beach City GIS employee's official Windows domain user account.
- **Server Environment:** ArcGIS Server `10.8.1` (unpatched End-Of-Life 2020 deployment running on IIS/10.0).
- **Vulnerability:** The server was deployed with broken token security. REST services and administrative panels (`/arcgis/admin`, `/arcgis/manager`, `/arcgis/tokens`) were publicly accessible without authentication.

### 2. Targeted Address & Parcel Modifications
User `NUWEYT` accessed the unauthenticated **`AddressEdits` FeatureServer**, executing SQL/REST database edits across 74 fields (`OWNERNAME1`, `MAILADDRESS`, `MAILSTATE`, `APN`, `LASTSALEVALTRANSFER`, `LASTDOCNUMBER`), specifically altering:

1. **Huntington Beach Navigation Center (HBNC) Parcel Entries:**
   - Address alterations on **17631 Cameron Lane** and **17642 Beach Blvd** — the city-acquired homeless facility properties situated directly over hexavalent chromium / environmental contamination plumes.
2. **Pham Family Real Property Holdings:**
   - Ownership and mailing address updates for **DDD PHAM LLC** (`19102` & `19142 Beach Blvd`) and adjacent commercial parcels along the Beach Blvd contamination corridor.
3. **Out-of-State Mail Drop Masking (160 Parcels):**
   - Altering mailing address attributes for **160 out-of-state owner parcels** to obscure virtual office drops used by PPP fraud shell networks, including:
     - **3225 McLeod Dr #777, Las Vegas, NV** (10 LLCs including `SUN AND FUN LLC`).
     - **5815 E Redfield Rd, Scottsdale, AZ** (4 `RE HOLDINGS` shells).
     - **1290 Avenue of the Americas, NYC** (`17531 Griffin Lane HB LLC` — 7 condo units, $14.7M value).

---

## III. LEGAL & EVIDENTIARY IMPLICATIONS

1. **Data Tampering & Official Records Alteration:**
   - Leaving the `AddressEdits` FeatureServer open with full `Create`, `Update`, `Delete`, `Uploads`, and `Editing` privileges allowed `NUWEYT` (or unauthorized parties acting under `NUWEYT` domain credentials) to modify municipal land records, title doc numbers, and tax mailing addresses without an audit trail.
2. **Cross-Reference to Federal Qui Tam Docket:**
   - Incorporating these forensic findings into CACD Case No. `8:26-cv-00348-JWH-ADS` demonstrates deliberate municipal record scrubbing surrounding contaminated properties and PPP fraud real estate holdings.

---

## IV. LINKED REPOSITORY ASSETS

- **[`agent/opencode_data_nofIV75K.txt`](https://github.com/Tonypost949/OsintNeoAi/blob/main/agent/opencode_data_nofIV75K.txt)** — Raw Session Log containing `NUWEYT` audit lines 1819-2196.
- **[`OPENCODE_FORENSIC_MASTER_EXTRACTION.md`](https://github.com/Tonypost949/OsintNeoAi/blob/main/OPENCODE_FORENSIC_MASTER_EXTRACTION.md)** — OpenCode Master Extraction Vault.
- **[`ARCGIS_SPATIAL_INTELLIGENCE_DOSSIER.md`](https://github.com/Tonypost949/OsintNeoAi/blob/main/ARCGIS_SPATIAL_INTELLIGENCE_DOSSIER.md)** — ArcGIS Spatial Reconnaissance Matrix.

---

*Forensic Analysis of "NUWEYT" Address Manipulation Complete | Makaveli Protocol August 2026*
