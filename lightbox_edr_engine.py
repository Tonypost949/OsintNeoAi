"""LightBox & EDR Master Environmental Intelligence Engine
Full API integration covering Parcels, Assessments, Structures, Zoning, and EDR Environmental Reports.
Official Documentation: https://lightbox.document360.io/docs/apis
Developer Portal: https://developer.lightboxre.com
"""

import os
import json
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional

BASE_URL = "https://api.lightboxre.com/v1"

class LightBoxEDREngine:
    def __init__(self, workspace_root: str = "C:\\OsintNeoAi"):
        self.root = Path(workspace_root)
        self.api_key = os.getenv("LIGHTBOX_API_KEY", "")
        self.edr_cache = self._load_local_edr_cache()

    def _load_local_edr_cache(self) -> List[Dict[str, Any]]:
        cached_records = []
        target_files = [
            "edr_all_gps_coordinates.json",
            "edr_gps_mapping_clean.json",
            "edr_gps_multiline_mapped.json",
            "edr_masked_address_log.json"
        ]
        for fname in target_files:
            fpath = self.root / fname
            if fpath.exists():
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            for row in data:
                                row["source_file"] = fname
                                cached_records.append(row)
                except Exception:
                    pass
        return cached_records

    def get_headers(self, custom_key: Optional[str] = None) -> Dict[str, str]:
        key = custom_key or self.api_key or os.getenv("LIGHTBOX_API_KEY", "")
        return {
            "x-api-key": key,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def get_summary_stats(self) -> Dict[str, Any]:
        unique_covers = set(r.get("cover_address", "").strip() for r in self.edr_cache if r.get("cover_address"))
        return {
            "total_cached_records": len(self.edr_cache),
            "unique_sites_audited": len(unique_covers),
            "live_api_active": bool(self.api_key)
        }

    def search_edr_records(self, query: str) -> List[Dict[str, Any]]:
        q_lower = query.lower()
        matches = []
        for r in self.edr_cache:
            cover = str(r.get("cover_address", "")).lower()
            fname = str(r.get("file", "")).lower()
            loc = str(r.get("real_physical_location", "")).lower()
            if q_lower in cover or q_lower in fname or q_lower in loc:
                matches.append(r)
        return matches

    # 1. Parcels API: Search by Address
    def search_parcel_by_address(self, address_text: str, custom_key: Optional[str] = None) -> Dict[str, Any]:
        url = f"{BASE_URL}/parcels/us/address"
        headers = self.get_headers(custom_key)
        try:
            resp = requests.get(url, headers=headers, params={"text": address_text}, timeout=15)
            return {"status_code": resp.status_code, "data": resp.json() if resp.status_code == 200 else resp.text}
        except Exception as e:
            return {"status_code": 500, "error": str(e)}

    # 2. Parcels API: Search by FIPS & APN
    def search_parcel_by_apn(self, fips: str, apn: str, custom_key: Optional[str] = None) -> Dict[str, Any]:
        url = f"{BASE_URL}/parcels/us/{fips}/{apn}"
        headers = self.get_headers(custom_key)
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            return {"status_code": resp.status_code, "data": resp.json() if resp.status_code == 200 else resp.text}
        except Exception as e:
            return {"status_code": 500, "error": str(e)}

    # 3. Assessment & Property Tax API
    def get_assessment_data(self, parcel_id: str, custom_key: Optional[str] = None) -> Dict[str, Any]:
        url = f"{BASE_URL}/assessments/us/parcel/{parcel_id}"
        headers = self.get_headers(custom_key)
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            return {"status_code": resp.status_code, "data": resp.json() if resp.status_code == 200 else resp.text}
        except Exception as e:
            return {"status_code": 500, "error": str(e)}

    # 4. Structures & Building Footprint API
    def get_structure_data(self, parcel_id: str, custom_key: Optional[str] = None) -> Dict[str, Any]:
        url = f"{BASE_URL}/structures/us/parcel/{parcel_id}"
        headers = self.get_headers(custom_key)
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            return {"status_code": resp.status_code, "data": resp.json() if resp.status_code == 200 else resp.text}
        except Exception as e:
            return {"status_code": 500, "error": str(e)}

    # 5. EDR Environmental Radius Reports API
    def fetch_edr_environmental_report(self, address_text: str, custom_key: Optional[str] = None) -> Dict[str, Any]:
        url = f"{BASE_URL}/edr/reports/address"
        headers = self.get_headers(custom_key)
        try:
            resp = requests.get(url, headers=headers, params={"text": address_text}, timeout=15)
            return {"status_code": resp.status_code, "data": resp.json() if resp.status_code == 200 else resp.text}
        except Exception as e:
            return {"status_code": 500, "error": str(e)}

    # 6. Zoning API
    def get_zoning_data(self, parcel_id: str, custom_key: Optional[str] = None) -> Dict[str, Any]:
        url = f"{BASE_URL}/zoning/us/parcel/{parcel_id}"
        headers = self.get_headers(custom_key)
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            return {"status_code": resp.status_code, "data": resp.json() if resp.status_code == 200 else resp.text}
        except Exception as e:
            return {"status_code": 500, "error": str(e)}
