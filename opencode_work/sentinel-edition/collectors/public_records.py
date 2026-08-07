"""
Public records collectors for US government data sources.
All free, no API keys required for core sources.
"""

import json
import re
from datetime import datetime
from typing import Any

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class NPPESCollector:
    """NPI Registry (National Plan & Provider Enumeration System) - healthcare provider lookup."""
    name = "nppes"
    BASE_URL = "https://npiregistry.cms.hhs.gov/api/"

    def __init__(self, config=None):
        self.config = config or {}

    def search(self, name: str = None, npi: str = None, city: str = None, state: str = None, limit: int = 50) -> dict:
        params = {"version": "2.1", "limit": limit}
        if name:
            params["enumeration_type"] = "NPI-1,NPI-2"
            parts = name.split()
            if len(parts) >= 2:
                params["first_name"] = parts[0]
                params["last_name"] = " ".join(parts[1:])
            else:
                params["organization_name"] = name
        if npi:
            params["number"] = npi
        if city:
            params["city"] = city
        if state:
            params["state"] = state

        try:
            resp = requests.get(self.BASE_URL, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return {
                "source": "nppes",
                "query": {"name": name, "npi": npi, "city": city, "state": state},
                "results": data.get("results", []),
                "result_count": data.get("result_count", 0),
            }
        except Exception as e:
            return {"error": str(e), "source": "nppes"}


class SECEDGARCollector:
    """SEC EDGAR - corporate filings and ownership data."""
    name = "sec_edgar"
    BASE_URL = "https://efts.sec.gov/LATEST"

    def __init__(self, config=None):
        self.config = config or {}
        self.headers = {"User-Agent": "Sentinel OSINT Research/1.0"}

    def search_company(self, query: str) -> dict:
        url = f"{self.BASE_URL}/search-index?q=%22{query}%22&dateRange=custom&startdt=2020-01-01&forms=10-K,10-Q,8-K"
        try:
            resp = requests.get(url, headers=self.headers, timeout=30)
            if resp.status_code == 200:
                return {"source": "sec_edgar", "query": query, "filings": resp.json()}
            return {"source": "sec_edgar", "query": query, "error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"error": str(e), "source": "sec_edgar"}

    def get_entity_filings(self, cik: str) -> dict:
        url = f"https://data.sec.gov/submissions/CIK{cik.zfill(10)}.json"
        try:
            resp = requests.get(url, headers=self.headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            recent = data.get("filings", {}).get("recent", {})
            forms = recent.get("form", [])[:20]
            dates = recent.get("filingDate", [])[:20]
            return {
                "source": "sec_edgar",
                "cik": cik,
                "company": data.get("name", ""),
                "filings": [{"form": f, "date": d} for f, d in zip(forms, dates)],
            }
        except Exception as e:
            return {"error": str(e), "source": "sec_edgar"}


class USASpendingCollector:
    """USASpending.gov - federal spending data."""
    name = "usaspending"
    BASE_URL = "https://api.usaspending.gov/api/v2"

    def __init__(self, config=None):
        self.config = config or {}

    def search_recipients(self, query: str, limit: int = 20) -> dict:
        url = f"{self.BASE_URL}/search/spending_by_category/recipient/"
        payload = {
            "filters": {"keywords": [query]},
            "category": "recipient_duns",
            "limit": limit,
        }
        try:
            resp = requests.post(url, json=payload, timeout=30)
            resp.raise_for_status()
            return {"source": "usaspending", "query": query, "results": resp.json().get("results", [])}
        except Exception as e:
            return {"error": str(e), "source": "usaspending"}

    def search_awards(self, query: str, limit: int = 20) -> dict:
        url = f"{self.BASE_URL}/search/spending_by_award/"
        payload = {
            "filters": {"keywords": [query], "time_period": [{"start_date": "2020-01-01", "end_date": "2026-12-31"}]},
            "fields": ["Award ID", "Recipient Name", "Award Amount", "Start Date", "End Date", "Awarding Agency"],
            "limit": limit,
            "page": 1,
            "sort": "Award Amount",
            "order": "desc",
        }
        try:
            resp = requests.post(url, json=payload, timeout=30)
            resp.raise_for_status()
            return {"source": "usaspending", "query": query, "awards": resp.json().get("results", [])}
        except Exception as e:
            return {"error": str(e), "source": "usaspending"}


class PACERCollector:
    """
    PACER (federal court records) - basic search.
    Note: PACER requires an account and charges per search.
    This provides the API structure; actual usage requires credentials.
    """
    name = "pacer"

    def __init__(self, config=None):
        self.config = config or {}
        self.pacer_key = config.get("pacer_key", "") if config else ""

    def search(self, query: str) -> dict:
        if not self.pacer_key:
            return {
                "source": "pacer",
                "status": "requires_credentials",
                "message": "PACER requires a PACER account. Register at pacer.uscourts.gov. Cost: $0.10/page.",
                "registration_url": "https://pacer.uscourts.gov/register",
                "query": query,
            }
        return {"source": "pacer", "status": "not_implemented", "message": "PACER API integration requires court-specific PACER endpoints."}


class PublicRecordsAggregator:
    """Aggregates results from all public record sources."""

    def __init__(self, config=None):
        self.config = config or {}
        self.collectors = {
            "nppes": NPPESCollector(config),
            "sec_edgar": SECEDGARCollector(config),
            "usaspending": USASpendingCollector(config),
            "pacer": PACERCollector(config),
        }

    def search_all(self, query: str) -> dict:
        results = {}
        for name, collector in self.collectors.items():
            try:
                if hasattr(collector, "search"):
                    results[name] = collector.search(query)
                elif hasattr(collector, "search_recipients"):
                    results[name] = collector.search_recipients(query)
            except Exception as e:
                results[name] = {"error": str(e)}
        return results

    def list_sources(self) -> list[dict]:
        return [
            {"name": "nppes", "description": "NPI Registry - Healthcare providers", "free": True, "api_key_required": False},
            {"name": "sec_edgar", "description": "SEC EDGAR - Corporate filings", "free": True, "api_key_required": False},
            {"name": "usaspending", "description": "USASpending.gov - Federal contracts", "free": True, "api_key_required": False},
            {"name": "pacer", "description": "Federal court records", "free": False, "api_key_required": True},
        ]
