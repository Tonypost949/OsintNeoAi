"""
Web-based OSINT collectors. Uses only stdlib + requests.
All collectors return structured data for ingestion into the Sentinel graph.
"""

import json
import re
import hashlib
from datetime import datetime
from typing import Any
from urllib.parse import urlparse, quote_plus

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class BaseCollector:
    name = "base"
    description = "Base collector"

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.session = requests.Session() if HAS_REQUESTS else None
        if self.session:
            self.session.headers.update({
                "User-Agent": "Sentinel-OSINT/1.0 (Research用途)"
            })

    def collect(self, query: str) -> dict:
        raise NotImplementedError

    def _safe_request(self, url: str, **kwargs) -> dict:
        if not self.session:
            return {"error": "requests library not installed. Run: pip install requests"}
        try:
            resp = self.session.get(url, timeout=30, **kwargs)
            resp.raise_for_status()
            return {"status": resp.status_code, "content": resp.text, "url": resp.url}
        except Exception as e:
            return {"error": str(e), "url": url}


class DuckDuckGoCollector(BaseCollector):
    """Search via DuckDuckGo HTML (no API key needed)."""
    name = "duckduckgo"
    description = "Web search via DuckDuckGo"

    def collect(self, query: str) -> dict:
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        result = self._safe_request(url)
        if "error" in result:
            return result
        links = re.findall(r'class="result__a" href="(.*?)"', result.get("content", ""))
        snippets = re.findall(r'class="result__snippet">(.*?)</a>', result.get("content", ""), re.DOTALL)
        results = []
        for i, link in enumerate(links[:10]):
            results.append({
                "url": link,
                "snippet": snippets[i].strip() if i < len(snippets) else "",
            })
        return {"query": query, "results": results, "source": "duckduckgo"}


class WaybackCollector(BaseCollector):
    """Query the Wayback Machine for historical snapshots."""
    name = "wayback"
    description = "Internet Archive Wayback Machine"

    def collect(self, query: str) -> dict:
        url = f"https://web.archive.org/cdx/search/cdx?url={quote_plus(query)}&output=json&limit=20"
        result = self._safe_request(url)
        if "error" in result:
            return result
        try:
            data = json.loads(result.get("content", "[]"))
            if len(data) > 1:
                headers = data[0]
                snapshots = [dict(zip(headers, row)) for row in data[1:]]
                return {"query": query, "snapshots": snapshots, "source": "wayback_machine"}
        except json.JSONDecodeError:
            pass
        return {"query": query, "snapshots": [], "source": "wayback_machine"}


class CrtShCollector(BaseCollector):
    """Certificate Transparency log search via crt.sh."""
    name = "crtsh"
    description = "Certificate Transparency search"

    def collect(self, query: str) -> dict:
        url = f"https://crt.sh/?q={quote_plus(query)}&output=json"
        result = self._safe_request(url)
        if "error" in result:
            return result
        try:
            certs = json.loads(result.get("content", "[]"))
            return {"query": query, "certificates": certs[:50], "source": "crt.sh"}
        except json.JSONDecodeError:
            return {"query": query, "certificates": [], "source": "crt.sh"}


class WHOISCollector(BaseCollector):
    """Basic WHOIS lookup via RDAP."""
    name = "rdap"
    description = "Domain WHOIS/RDAP lookup"

    def collect(self, query: str) -> dict:
        domain = query.strip().lower()
        domain = re.sub(r'^https?://', '', domain)
        domain = domain.split('/')[0]
        url = f"https://rdap.org/domain/{domain}"
        result = self._safe_request(url)
        if "error" in result:
            return result
        try:
            data = json.loads(result.get("content", "{}"))
            return {"query": query, "whois": data, "source": "rdap"}
        except json.JSONDecodeError:
            return {"query": query, "whois": {}, "source": "rdap"}


class AbuseIPDBCollector(BaseCollector):
    """IP reputation lookup via AbuseIPDB (needs API key)."""
    name = "abuseipdb"
    description = "IP abuse reputation check"

    def collect(self, query: str) -> dict:
        api_key = self.config.get("abuseipdb_api_key")
        if not api_key:
            return {"error": "AbuseIPDB API key required. Set abuseipdb_api_key in config."}
        url = f"https://api.abuseipdb.com/api/v2/check"
        headers = {"Key": api_key, "Accept": "application/json"}
        params = {"ipAddress": query, "maxAgeInDays": 90}
        if self.session:
            try:
                resp = self.session.get(url, headers=headers, params=params, timeout=30)
                resp.raise_for_status()
                return {"query": query, "reputation": resp.json(), "source": "abuseipdb"}
            except Exception as e:
                return {"error": str(e)}
        return {"error": "requests library not installed"}


class ShodanCollector(BaseCollector):
    """Shodan IoT search (needs API key)."""
    name = "shodan"
    description = "Shodan IoT/device search"

    def collect(self, query: str) -> dict:
        api_key = self.config.get("shodan_api_key")
        if not api_key:
            return {"error": "Shodan API key required. Set shodan_api_key in config."}
        url = f"https://api.shodan.io/shodan/host/search?key={api_key}&query={quote_plus(query)}"
        result = self._safe_request(url)
        if "error" in result:
            return result
        try:
            data = json.loads(result.get("content", "{}"))
            return {"query": query, "matches": data.get("matches", [])[:20], "total": data.get("total", 0), "source": "shodan"}
        except json.JSONDecodeError:
            return {"query": query, "matches": [], "source": "shodan"}


class CollectorManager:
    """Manages all available collectors."""

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.collectors = {}
        self._register_builtin()

    def _register_builtin(self):
        for cls in [DuckDuckGoCollector, WaybackCollector, CrtShCollector, WHOISCollector]:
            self.collectors[cls.name] = cls(self.config)
        for cls in [AbuseIPDBCollector, ShodanCollector]:
            self.collectors[cls.name] = cls(self.config)

    def register(self, collector: BaseCollector):
        self.collectors[collector.name] = collector

    def run(self, collector_name: str, query: str) -> dict:
        if collector_name not in self.collectors:
            return {"error": f"Unknown collector: {collector_name}. Available: {list(self.collectors.keys())}"}
        return self.collectors[collector_name].collect(query)

    def run_all(self, query: str) -> dict:
        results = {}
        for name, collector in self.collectors.items():
            results[name] = collector.collect(query)
        return results

    def list_collectors(self) -> list[dict]:
        return [{"name": c.name, "description": c.description} for c in self.collectors.values()]
