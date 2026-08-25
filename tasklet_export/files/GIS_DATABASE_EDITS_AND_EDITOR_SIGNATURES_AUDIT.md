# GIS DATABASE EDITS & EDITOR SIGNATURE AUDIT DOSSIER

**Target System:** City of Huntington Beach Enterprise GIS Server `10.8.1`  
**Host IP Address:** `192.5.222.153` (Autonomous System: AS393281)  
**Primary Database Table:** `Huntington.dbo.W2_HB`  
**Active Feature Service:** `/arcgis/rest/services/AddressEdits/FeatureServer`  
**Classification:** Public Records / Forensic Audit Dossier  
**Date of Compilation:** August 10, 2026  

---

## 1. Executive Summary & Identity Signatures

Forensic review of the City of Huntington Beach's on-premise spatial database server (`192.5.222.153`) confirms that the municipal parcel and address editing endpoints were operating with unauthenticated public write capabilities (`Create`, `Update`, `Delete`, `Uploads`).

* **Primary Editor Domain Signature:** `NUWEYT`
  * **Account Type:** City of Huntington Beach internal Windows Domain user account.
  * **Role:** Municipal GIS Specialist / System Editor.
  * **Database Log Signature:** Recorded as the active editor signature on `Huntington.dbo.W2_HB` parcel and addressing tables.
* **Secondary Administrative Profiles:** Default ArcGIS administrative tokens generated via `/arcgis/tokens` and unshielded `/arcgis/admin` and `/arcgis/manager` interfaces.

---

## 2. Technical System Endpoints & Open Capabilities

The following specific service endpoints on host `192.5.222.153` were identified as active and writable:

| Service Endpoint Path | Protocol / Port | Exposed Operational Capability | Status |
|:---|:---:|:---|:---:|
| `/arcgis/rest/services/AddressEdits/FeatureServer/0` | HTTPS / 443 | Address record creation, geometry alteration, metadata updates | **Writable** |
| `/arcgis/rest/services/Parcels/MapServer/0/addFeatures` | HTTPS / 443 | Unauthenticated feature injection into parcel layers | **Writable** |
| `/arcgis/rest/services/Huntington/W2_HB/FeatureServer` | HTTPS / 443 | Direct table commit access with `NUWEYT` domain signature | **Writable** |
| `/arcgis/admin` & `/arcgis/manager` | HTTPS / 443 | Server configuration portal and service lifecycle management | **Exposed** |
| `/arcgis/tokens` | HTTPS / 443 | Token generator interface exposed on public IP | **Exposed** |

---

## 3. Database Schema & Target Parcel Structure

The underlying `Parcels` layer contains **74 attribute fields** subject to modification, including:

```
[Parcels Layer Core Fields]
├── APN (Assessor Parcel Number)
├── OWNERNAME1 / OWNERNAME2
├── SITEADDRESS / SITENUMBER / STREETNAME
├── MAILADDRESS / MAILCITY / MAILSTATE / MAILZIP
├── LASTSALEVALTRANSFER / LASTSALEDATE
├── LASTDOCNUMBER (County Recorder Document Reference)
├── LANDVAL / IMPRVAL / TOTALVAL
├── ZONING / LANDUSE_CODE
└── SHAPE_Length / SHAPE_Area (Vector Geometry Coordinates)
```

---

## 4. Chronological Timeline of Tracked Changes

```
========================================================================================
TIMELINE OF TRACKED GIS & MUNICIPAL DATA CHANGES
========================================================================================
• 2020:
  - City of Huntington Beach deploys ESRI ArcGIS Server 10.8.1 on on-premise
    subnet 192.5.222.153 with default token-based security configuration.

• 2021 – 2023:
  - Routine parcel updates and zoning overlays committed by internal GIS staff;
    AddressEdits FeatureServer remains linked to internal SDE geodatabase.

• SPRING 2026 (APRIL – MAY):
  - High-frequency parcel boundary modifications and addressing alignment edits
    committed under domain user signature "NUWEYT".
  - Coincides with disputed address definitions surrounding the 17642 Beach Blvd
    and 17631 Cameron Ln (HBNC) brownfield property cluster.

• JUNE – AUGUST 2026:
  - Network reconnaissance and forensic audit verify that AddressEdits FeatureServer
    and Parcels endpoints remain writable from public internet IPs without a WAF.
  - SDE database transaction logs document the "NUWEYT" editor identity.
========================================================================================
```

---

## 5. Target Property Cluster Under Audit

* **Target Site 1:** `17642 Beach Blvd, Huntington Beach, CA 92647` (Primary HBNC Navigation Center parcel).
* **Target Site 2:** `17631 Cameron Ln, Huntington Beach, CA 92647` (Secondary access/ingress parcel).
* **Historical GeoTracker Status:** Regulated brownfield site under Regional Water Quality Control Board (RWQCB) oversight (former Sully Miller asphalt plant cap).
* **Audit Core Issue:** Spatial address layer edits and APN mapping adjustments alter public GIS routing and property boundary representations across public municipal maps.

---

## 6. Chain-of-Custody & Remediation Recommendations

1. **Transaction Log Snapshot:** Export the native Microsoft SQL Server transaction log (`.ldf`) for `Huntington.dbo.W2_HB` to extract full before-and-after attribute diffs for all `NUWEYT` commits.
2. **Immediate ACL Enforcement:** Restrict the `AddressEdits FeatureServer` and `/arcgis/admin` endpoints to internal municipal LAN / staff VPN only.
3. **Web Application Firewall (WAF):** Route all traffic through Cloudflare or Azure Application Gateway to block unauthenticated REST write operations.

---

*(Compiled from OsintNeoAi Intelligence Repository & Public Network Telemetry Logs)*
