# 🏢 LIGHTBOX RE API (`developer.lightboxre.com`) INTEGRATION GUIDE

**Relator / Architect:** Anthony Michael DeMarcello III  
**Portal:** [`https://developer.lightboxre.com`](https://developer.lightboxre.com)  
**Connector Script:** [`agent/lightbox_connector.py`](https://github.com/Tonypost949/OsintNeoAi/blob/main/agent/lightbox_connector.py)  
**Status:** READY FOR API KEY PASTE  
**Date:** August 07, 2026  

---

## 🔑 HOW TO CONFIGURE YOUR LIGHTBOX API KEY

When you generate or copy your new API key from **[`developer.lightboxre.com`](https://developer.lightboxre.com)**, you can activate it instantly using any of the following methods:

### Method 1: Environment Variable (Recommended for PowerShell / CMD)
```powershell
$env:LIGHTBOX_API_KEY="YOUR_NEW_LIGHTBOX_API_KEY_HERE"
python agent/lightbox_connector.py 102-121-04
```

### Method 2: Pass Direct to Local Script
```bash
python agent/lightbox_connector.py --key YOUR_NEW_LIGHTBOX_API_KEY_HERE
```

---

## 🎯 DATA ENDPOINTS INCLUDED IN HARNESS

1. **Parcels API (`/v1/parcels/us`):** Real-time APN, tax assessment, land value, zoning code, and ownership entity queries.
2. **EDR Environmental Risk Reports (`/v1/edr/reports`):** Query historical EDR radius reports for contaminated sites (e.g. `17631 Cameron Ln` & `17642 Beach Blvd`).
3. **Assessment Geometry API:** GeoJSON parcel boundaries for direct integration into Leaflet / ArcGIS Web Maps (`hbnc_rico_gis.html`).

---

*LightBox RE API Integration Architecture Ready | Makaveli Protocol August 2026*
