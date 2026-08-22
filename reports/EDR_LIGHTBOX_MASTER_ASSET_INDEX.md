# 🏢 EDR & LightBox Master Environmental Asset & Forensics Index

Comprehensive inventory of all **EDR Environmental Risk Reports**, **Certified Sanborn Maps**, **LightBox RE API Harnesses**, and **Google Drive Evidence Links** across the OSINTNeoAi repository.

---

## 🔗 I. Developer Portals & Official Documentation

* 🌐 **LightBox Developer Portal:** [https://developer.lightboxre.com](https://developer.lightboxre.com)
* 🔑 **Personal App Management:** [https://developer.lightboxre.com/apps/personal/lightbox/details](https://developer.lightboxre.com/apps/personal/lightbox/details)
* 📚 **Official LightBox API Docs:** [https://lightbox.document360.io/docs/apis](https://lightbox.document360.io/docs/apis)
* 📑 **LightBox Integration Guide:** [`LIGHTBOX_RE_INTEGRATION_GUIDE.md`](https://github.com/Tonypost949/OsintNeoAi/blob/main/LIGHTBOX_RE_INTEGRATION_GUIDE.md)

---

## 📂 II. Indexed EDR Datasets & GPS Coordinates (Local Archives)

| Dataset | Records | Description | Full Path |
| :--- | :--- | :--- | :--- |
| **`edr_all_gps_coordinates.json`** | **303** | Full GPS & address mapping extracted from commercial EDR radius PDFs | [`edr_all_gps_coordinates.json`](https://github.com/Tonypost949/OsintNeoAi/blob/main/edr_all_gps_coordinates.json) |
| **`edr_gps_mapping_clean.json`** | **310** | Sanitized Sanborn map coordinates and physical location descriptors | [`edr_gps_mapping_clean.json`](https://github.com/Tonypost949/OsintNeoAi/blob/main/edr_gps_mapping_clean.json) |
| **`edr_masked_address_log.json`** | **260** | Masked address extraction logs and GeoServices LLC disclosures | [`edr_masked_address_log.json`](https://github.com/Tonypost949/OsintNeoAi/blob/main/edr_masked_address_log.json) |
| **`edr_gps_multiline_mapped.json`** | **150+** | Multi-line parcel and property address strings | [`edr_gps_multiline_mapped.json`](https://github.com/Tonypost949/OsintNeoAi/blob/main/edr_gps_multiline_mapped.json) |

---

## 🎯 III. Key Audited Environmental Target Sites

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

## 🛠️ IV. Processing Scripts & Connectors

* 🚀 **Master Engine:** [`lightbox_edr_engine.py`](https://github.com/Tonypost949/OsintNeoAi/blob/main/lightbox_edr_engine.py) (11-endpoint API suite)
* ⚡ **Batch Audit Script:** [`run_lightbox_batch_audit.py`](https://github.com/Tonypost949/OsintNeoAi/blob/main/run_lightbox_batch_audit.py)
* 🔍 **Drive EDR Link Extractor:** [`opencode_work/edr_links.py`](https://github.com/Tonypost949/OsintNeoAi/blob/main/opencode_work/edr_links.py)
* 📑 **Commercial Report Scanner:** [`opencode_work/find_real_edr.py`](https://github.com/Tonypost949/OsintNeoAi/blob/main/opencode_work/find_real_edr.py)
* 📡 **LightBox Gateway Monitor:** [`agent/monitor_lightbox_gateway.py`](https://github.com/Tonypost949/OsintNeoAi/blob/main/agent/monitor_lightbox_gateway.py)
* 🏢 **Legacy Connector:** [`agent/lightbox_connector.py`](https://github.com/Tonypost949/OsintNeoAi/blob/main/agent/lightbox_connector.py)

---

## 🔒 V. Cloud Database & BigQuery Evidence Mapping

* **Data Warehouse Project:** `noble-beanbag-497411-m4` / `project-743aab84-f9a5-4ec7-954`
* **Tables Indexed:**
  * `national_audits.drive_file_index` (Over 1M+ Google Drive records indexed)
  * `national_audits.local_scan_extracted_text`
  * `national_audits.local_scan_matches`
  * `ppp_rico.city_cyber_recon`
  * `ppp_rico.trafficking_matches`

---
*Cryptographic Integrity Standard: NIST SHA-256 Checksums applied to all master files.*
