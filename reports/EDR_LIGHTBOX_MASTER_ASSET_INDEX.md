# 🏢 EDR & LightBox Master Environmental Asset & Forensics Index

Comprehensive inventory of all **EDR Environmental Risk Reports**, **EDRnet Order Portals**, **Certified Sanborn Maps**, **GeoTracker Environmental Case Profiles**, and **Nevada / Desert GPS Coordinates** across the OSINTNeoAi repository.

---

## 🔗 I. Developer Portals, Order Tracking & Official Bookmarks

* 🌐 **LightBox Developer Portal:** [https://developer.lightboxre.com](https://developer.lightboxre.com)
* 🔑 **Personal App Management:** [https://developer.lightboxre.com/apps/personal/lightbox/details](https://developer.lightboxre.com/apps/personal/lightbox/details)
* 📚 **Official LightBox API Docs:** [https://lightbox.document360.io/docs/apis](https://lightbox.document360.io/docs/apis)
* 📑 **LightBox Integration Guide:** [`LIGHTBOX_RE_INTEGRATION_GUIDE.md`](https://github.com/Tonypost949/OsintNeoAi/blob/main/LIGHTBOX_RE_INTEGRATION_GUIDE.md)
* 📦 **EDRnet Live Order Status Portal (Session 1):** [web.edrnet.com/Ordering/OrderStatus](https://www.web.edrnet.com/Ordering/OrderStatus/status.aspx?O=1&lsessguid=7ce4ba6b-006c-4314-9e5f-81fcaa9f8aed)
* 📦 **EDRnet Live Order Status Portal (Session 2):** [web.edrnet.com/Ordering/OrderStatus](https://www.web.edrnet.com/Ordering/OrderStatus/status.aspx?lsessguid=8772a597-d32d-4ef8-96fc-2c2f472809aa)
* 🔍 **ParcelQuest Statewide Real Estate Property Search:** [assr.parcelquest.com/Statewide](https://assr.parcelquest.com/Statewide/Estimate/0)
* 💧 **GeoTracker Water Quality Well Report (`W0603000618`):** [geotracker.waterboards.ca.gov](https://geotracker.waterboards.ca.gov/regulators/reports/well_quality.asp?global_id=W0603000618&assigned_name=CA3000618_001_001&allrecords=on)
* ☣️ **GeoTracker Case Profile Report (`T10000020555`):** [geotracker.waterboards.ca.gov/profile_report](https://geotracker.waterboards.ca.gov/profile_report.asp?global_id=T10000020555)

---

## 📍 II. Nevada Desert & MGM Grand GPS Spatial Coordinate Hubs

When street addresses are unassigned, raw desert parcels, or mismatched in legacy EDR documents, the system queries exact GPS coordinates:

* 🎰 **MGM Grand Las Vegas Hub:** `36.1026° N, 115.1703° W` (3799 S Las Vegas Blvd, Clark County, NV)
* 🏜️ **Apex Desert Industrial Corridor:** `36.3150° N, 114.9200° W` (Clark County, NV)
* ⛏️ **Nye County Mining / Testing Corridor:** `36.9092° N, 116.7547° W` (Beatty Corridor, NV)
* 🏭 **Tahoe-Reno / Storey County Industrial:** `39.5296° N, 119.8138° W` (USA Pkwy, NV)

---

## 📂 III. Indexed EDR Datasets & GPS Coordinates (Local Archives)

| Dataset | Records | Description | Full Path |
| :--- | :--- | :--- | :--- |
| **`edr_all_gps_coordinates.json`** | **303** | Full GPS & address mapping extracted from commercial EDR radius PDFs | [`edr_all_gps_coordinates.json`](https://github.com/Tonypost949/OsintNeoAi/blob/main/edr_all_gps_coordinates.json) |
| **`edr_gps_mapping_clean.json`** | **310** | Sanitized Sanborn map coordinates and physical location descriptors | [`edr_gps_mapping_clean.json`](https://github.com/Tonypost949/OsintNeoAi/blob/main/edr_gps_mapping_clean.json) |
| **`edr_masked_address_log.json`** | **260** | Masked address extraction logs and GeoServices LLC disclosures | [`edr_masked_address_log.json`](https://github.com/Tonypost949/OsintNeoAi/blob/main/edr_masked_address_log.json) |
| **`edr_gps_multiline_mapped.json`** | **150+** | Multi-line parcel and property address strings | [`edr_gps_multiline_mapped.json`](https://github.com/Tonypost949/OsintNeoAi/blob/main/edr_gps_multiline_mapped.json) |

---

## 🎯 IV. Key Audited Environmental Target Sites

### 1. 📍 Vagabond Inn / Casa Aliento (`17642 Beach Blvd, Huntington Beach, CA`)
* **EDR Inquiry / Order Numbers:** `7887036.12_1`, `7887036.3`, `7887036.4`
* **Local Matches:** **28 Audited Sanborn & Radius Report Files**
* **Environmental Context:** Toxic plume / soil vapor remediation records adjacent to Ascon Landfill & homeless shelter site.

### 2. 📍 Cameron Lane Property Hub (`17631 Cameron Ln, Huntington Beach, CA`)
* **EDR Inquiry / Order Numbers:** `7887036.15`, `7887036.16`, `7887036.24_1`, `788703618`
* **Local Matches:** **15 Audited Report Files**
* **Environmental Context:** Historical agricultural pesticide/solvent disclosures.

### 3. 📍 Garden Grove Asset (`13252 Garden Grove Blvd, Garden Grove, CA`)
* **EDR Inquiry / Order Numbers:** `074-0125-014_Sanborn_7867953.3S`
* **Local Matches:** **2 Sanborn Historical Maps**

---

## 🛠️ V. Processing Scripts & Connectors

* 🚀 **Master Engine:** [`lightbox_edr_engine.py`](https://github.com/Tonypost949/OsintNeoAi/blob/main/lightbox_edr_engine.py) (11-endpoint API suite)
* ⚡ **Batch Audit Script:** [`run_lightbox_batch_audit.py`](https://github.com/Tonypost949/OsintNeoAi/blob/main/run_lightbox_batch_audit.py)
* 🔍 **Drive EDR Link Extractor:** [`opencode_work/edr_links.py`](https://github.com/Tonypost949/OsintNeoAi/blob/main/opencode_work/edr_links.py)
* 📑 **Commercial Report Scanner:** [`opencode_work/find_real_edr.py`](https://github.com/Tonypost949/OsintNeoAi/blob/main/opencode_work/find_real_edr.py)
* 📡 **LightBox Gateway Monitor:** [`agent/monitor_lightbox_gateway.py`](https://github.com/Tonypost949/OsintNeoAi/blob/main/agent/monitor_lightbox_gateway.py)
* 🏢 **Legacy Connector:** [`agent/lightbox_connector.py`](https://github.com/Tonypost949/OsintNeoAi/blob/main/agent/lightbox_connector.py)

---
*Cryptographic Integrity Standard: NIST SHA-256 Checksums applied to all master files.*
