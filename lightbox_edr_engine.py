"""LightBox & EDR Master Environmental Intelligence Engine
Fuses local EDR radius reports, Sanborn map indices, and live LightBox RE API calls.
"""

import os
import json
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional

LIGHTBOX_API_KEY = os.getenv("LIGHTBOX_API_KEY", "")
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

    def query_live_parcel(self, address_text: str) -> Optional[Dict[str, Any]]:
        if not self.api_key:
            return None
        headers = {
            "x-api-key": self.api_key,
            "Accept": "application/json"
        }
        url = f"{BASE_URL}/parcels/us/address"
        try:
            resp = requests.get(url, headers=headers, params={"text": address_text}, timeout=10)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None
