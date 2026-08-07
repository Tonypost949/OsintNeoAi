# 🏢 LIGHTBOX RE PROPERTY & EDR PARCEL CONNECTOR ENGINE

**Relator / Architect:** Anthony Michael DeMarcello III  
**API Portal:** [`https://developer.lightboxre.com`](https://developer.lightboxre.com)  
**Target Capabilities:** EDR Environmental Reports, Assessment Parcels, Land Ownership Vectors  
**Configuration Script:** [`agent/lightbox_connector.py`](https://github.com/Tonypost949/OsintNeoAi/blob/main/agent/lightbox_connector.py)  
**Date:** August 07, 2026  

---

## I. EXECUTIVE OVERVIEW

The LightBox RE API (`developer.lightboxre.com`) connects EDR environmental historical records, real estate parcel geometry, structure boundary data, and nationwide tax assessor records directly into the OSINT Neo AI BigQuery and GIS map visualization engines.

```mermaid
graph TD
    subgraph LIGHTBOX_API_PORTAL["LightBox Developer Portal (developer.lightboxre.com)"]
        L1["API Key Authentication<br>(LIGHTBOX_API_KEY)"]
        L2["EDR Environmental Data Endpoint<br>(/v1/edr/reports)"]
        L3["Parcels & Assessment Endpoint<br>(/v1/parcels/us)"]
    end

    subgraph OSINT_NEO_AI_PIPELINE["OSINT Neo AI Ingestion Pipeline"]
        P1["LightBox Connector Engine<br>(agent/lightbox_connector.py)"]
        P2["BigQuery Evidence Vault<br>(national_audits.lightbox_parcels)"]
        P3["Interactive Recon Map<br>(hbnc_rico_gis.html)"]
    end

    L1 --> P1
    L2 --> P1
    L3 --> P1
    P1 --> P2
    P1 --> P3
```

---

## II. LIGHTBOX API CONNECTOR ENGINE (`agent/lightbox_connector.py`)

```python
"""
lightbox_connector.py — LightBox RE API Integration Engine
-----------------------------------------------------------
Connects developer.lightboxre.com API keys to fetch EDR environmental 
reports and real estate parcel assessment layers for target APNs.
"""

import os
import sys
import json
import requests

LIGHTBOX_API_KEY = os.environ.get("LIGHTBOX_API_KEY", "")
BASE_URL = "https://api.lightboxre.com/v1"

def fetch_parcel_by_apn(apn, state="CA", county="Orange"):
    """Fetch structured parcel assessment record from LightBox RE API."""
    if not LIGHTBOX_API_KEY:
        print("⚠️ LIGHTBOX_API_KEY environment variable not set.")
        print("  Register / Regenerate key at: https://developer.lightboxre.com")
        return None

    headers = {
        "x-api-key": LIGHTBOX_API_KEY,
        "Content-Type": "application/json"
    }
    
    url = f"{BASE_URL}/parcels/us/{state}/{county}/{apn}"
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"Connection failed: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_apn = sys.argv[1]
        print(f"Fetching LightBox record for APN: {target_apn}...")
        res = fetch_parcel_by_apn(target_apn)
        if res:
            print(json.dumps(res, indent=2))
    else:
        print("LightBox RE API Connector initialized. Awaiting LIGHTBOX_API_KEY input.")
