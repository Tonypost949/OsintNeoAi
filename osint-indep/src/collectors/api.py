"""
API integrations collector for OSINT Independent Platform.
Handles Shodan, VirusTotal, Censys, SecurityTrails, Hunter.io, GitHub, etc.
"""
import asyncio
import hashlib
import hmac
import json
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import aiohttp

from .base import BaseCollector, CollectorResult, collector
from ..core.models import Entity, EntityType, Observation, Source, SourceType, ConfidenceLevel


@collector(
    name="shodan",
    description="Shodan internet intelligence",
    supported_types=[EntityType.IP, EntityType.DOMAIN, EntityType.ASN],
    rate_limit=60,
    timeout=30
)
class ShodanCollector(BaseCollector):
    """Shodan API integration."""
    
    BASE_URL = "https://api.shodan.io"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.api_key = self.collectors.api_keys.get('shodan', '')
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        return self.session
    
    async def collect(self, target: str, **kwargs) -> CollectorResult:
        """Collect Shodan intelligence."""
        if not self.api_key:
            return CollectorResult(errors=["Shodan API key not configured"])
        
        await self._wait_for_rate_limit()
        job = self._start_job(target, kwargs)
        result = CollectorResult()
        
        try:
            if self._is_ip(target):
                await self._collect_host(target, result)
            elif self._is_domain(target):
                await self._collect_domain(target, result)
            elif self._is_asn(target):
                await self._collect_asn(target, result)
        except Exception as e:
            self.logger.error(f"Shodan collection failed for {target}: {e}")
            result.errors.append(str(e))
        finally:
            self._complete_job(result)
        
        return result
    
    async def _collect_host(self, ip: str, result: CollectorResult) -> None:
        """Collect Shodan host data for an IP."""
        session = await self._get_session()
        url = f"{self.BASE_URL}/shodan/host/{ip}"
        params = {'key': self.api_key, 'minify': True}
        
        async with session.get(url, params=params) as resp:
            if resp.status == 404:
                return
            data = await resp.json()
        
        ip_entity = self._create_entity(
            EntityType.IP, ip,
            source_name="shodan",
            source_type=SourceType.API,
            attributes={'shodan': True}
        )
        result.entities.append(ip_entity)
        
        # Ports and services
        for port_data in data.get('data', []):
            port = port_data.get('port')
            product = port_data.get('product', '')
            version = port_data.get('version', '')
            vulns = port_data.get('vulns', {})
            
            obs = self._create_observation(ip_entity.id, {
                'type': 'shodan_service',
                'port': port,
                'protocol': port_data.get('transport', 'tcp'),
                'product': product,
                'version': version,
                'banner': port_data.get('data', '')[:500],
                'vulnerabilities': list(vulns.keys()) if vulns else [],
                'location': port_data.get('location', {}),
                'timestamp': port_data.get('timestamp')
            })
            result.observations.append(obs)
        
        # Hostnames
        for hostname in data.get('hostnames', []):
            host_entity = self._create_entity(
                EntityType.DOMAIN, hostname,
                source_name="shodan",
                source_type=SourceType.API,
                attributes={'source': 'shodan_hostname'}
            )
            result.entities.append(host_entity)
            result.relationships.append({
                'source_id': host_entity.id,
                'target_id': ip_entity.id,
                'relationship_type': 'resolves_to',
                'description': f'{hostname} resolves to {ip} (via Shodan)'
            })
        
        # Vulnerabilities
        for vuln_id, vuln_data in data.get('vulns', {}).items():
            obs = self._create_observation(ip_entity.id, {
                'type': 'shodan_vulnerability',
                'vulnerability_id': vuln_id,
                'cvss': vuln_data.get('cvss'),
                'summary': vuln_data.get('summary', '')[:500]
            })
            result.observations.append(obs)
    
    async def _collect_domain(self, domain: str, result: CollectorResult) -> None:
        """Collect Shodan domain data."""
        session = await self._get_session()
        url = f"{self.BASE_URL}/dns/domain/{domain}"
        params = {'key': self.api_key}
        
        async with session.get(url, params=params) as resp:
            if resp.status == 404:
                return
            data = await resp.json()
        
        domain_entity = self._create_entity(
            EntityType.DOMAIN, domain,
            source_name="shodan",
            source_type=SourceType.API,
            attributes={'shodan': True}
        )
        result.entities.append(domain_entity)
        
        for record in data.get('data', []):
            subdomain = record.get('subdomain')
            if subdomain:
                full_domain = f"{subdomain}.{domain}"
                sub_entity = self._create_entity(
                    EntityType.DOMAIN, full_domain,
                    source_name="shodan",
                    source_type=SourceType.API,
                    attributes={'source': 'shodan_dns', 'type': record.get('type')}
                )
                result.entities.append(sub_entity)
                
                if record.get('value'):
                    ip_entity = self._create_entity(
                        EntityType.IP, record['value'],
                        source_name="shodan",
                        source_type=SourceType.API,
                        attributes={'source': 'shodan_dns', 'record_type': record.get('type')}
                    )
                    result.entities.append(ip_entity)
                    result.relationships.append({
                        'source_id': sub_entity.id,
                        'target_id': ip_entity.id,
                        'relationship_type': 'resolves_to',
                        'description': f'{full_domain} {record.get("type")} {record["value"]}'
                    })
    
    async def _collect_asn(self, asn: str, result: CollectorResult) -> None:
        """Collect Shodan ASN data."""
        session = await self._get_session()
        asn_num = asn.replace('AS', '')
        url = f"{self.BASE_URL}/shodan/asn/{asn_num}"
        params = {'key': self.api_key}
        
        async with session.get(url, params=params) as resp:
            if resp.status == 404:
                return
            data = await resp.json()
        
        asn_entity = self._create_entity(
            EntityType.ASN, asn,
            source_name="shodan",
            source_type=SourceType.API,
            attributes={'shodan': True}
        )
        result.entities.append(asn_entity)
        
        # Add IP ranges
        for prefix in data.get('prefixes', []):
            obs = self._create_observation(asn_entity.id, {
                'type': 'shodan_prefix',
                'prefix': prefix.get('prefix'),
                'description': prefix.get('description', '')
            })
            result.observations.append(obs)
    
    def _is_ip(self, target: str) -> bool:
        import re
        return re.match(r'^(\d{1,3}\.){3}\d{1,3}$', target) is not None
    
    def _is_domain(self, target: str) -> bool:
        import re
        return re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$', target) is not None
    
    def _is_asn(self, target: str) -> bool:
        import re
        return re.match(r'^AS?\d+$', target, re.IGNORECASE) is not None


@collector(
    name="virustotal",
    description="VirusTotal file, URL, domain, IP intelligence",
    supported_types=[EntityType.FILE, EntityType.URL, EntityType.DOMAIN, EntityType.IP],
    rate_limit=4,
    timeout=30
)
class VirusTotalCollector(BaseCollector):
    """VirusTotal API integration."""
    
    BASE_URL = "https://www.virustotal.com/api/v3"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.api_key = self.collectors.api_keys.get('virustotal', '')
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            headers = {'x-apikey': self.api_key} if self.api_key else {}
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        return self.session
    
    async def collect(self, target: str, **kwargs) -> CollectorResult:
        if not self.api_key:
            return CollectorResult(errors=["VirusTotal API key not configured"])
        
        await self._wait_for_rate_limit()
        job = self._start_job(target, kwargs)
        result = CollectorResult()
        
        try:
            if self._is_hash(target):
                await self._collect_file(target, result)
            elif self._is_url(target):
                await self._collect_url(target, result)
            elif self._is_domain(target):
                await self._collect_domain(target, result)
            elif self._is_ip(target):
                await self._collect_ip(target, result)
        except Exception as e:
            result.errors.append(str(e))
        finally:
            self._complete_job(result)
        
        return result
    
    async def _collect_file(self, file_hash: str, result: CollectorResult) -> None:
        session = await self._get_session()
        url = f"{self.BASE_URL}/files/{file_hash}"
        
        async with session.get(url) as resp:
            if resp.status == 404:
                return
            data = await resp.json()
        
        attrs = data.get('data', {}).get('attributes', {})
        
        file_entity = self._create_entity(
            EntityType.FILE, file_hash,
            source_name="virustotal",
            source_type=SourceType.API,
            attributes={'vt_data': True}
        )
        result.entities.append(file_entity)
        
        # Malicious stats
        stats = attrs.get('last_analysis_stats', {})
        if stats.get('malicious', 0) > 0:
            file_entity.is_malicious = True
            file_entity.risk_score = min(100, stats['malicious'] * 10)
        
        result.observations.append(self._create_observation(file_entity.id, {
            'type': 'virustotal_file',
            'hash': file_hash,
            'stats': stats,
            'type_description': attrs.get('type_description'),
            'meaningful_name': attrs.get('meaningful_name'),
            'size': attrs.get('size'),
            'trid': attrs.get('trid', []),
            'pe_info': attrs.get('pe_info', {})
        }))
        
        # Relationships
        for contact in attrs.get('contacted_domains', []):
            dom_entity = self._create_entity(EntityType.DOMAIN, contact, source_name="virustotal", source_type=SourceType.API)
            result.entities.append(dom_entity)
            result.relationships.append({
                'source_id': file_entity.id,
                'target_id': dom_entity.id,
                'relationship_type': 'contacts',
                'description': f'File {file_hash} contacts {contact}'
            })
        
        for contact in attrs.get('contacted_ips', []):
            ip_entity = self._create_entity(EntityType.IP, contact, source_name="virustotal", source_type=SourceType.API)
            result.entities.append(ip_entity)
            result.relationships.append({
                'source_id': file_entity.id,
                'target_id': ip_entity.id,
                'relationship_type': 'contacts',
                'description': f'File {file_hash} contacts {contact}'
            })
    
    async def _collect_domain(self, domain: str, result: CollectorResult) -> None:
        session = await self._get_session()
        url = f"{self.BASE_URL}/domains/{domain}"
        
        async with session.get(url) as resp:
            if resp.status == 404:
                return
            data = await resp.json()
        
        attrs = data.get('data', {}).get('attributes', {})
        
        domain_entity = self._create_entity(
            EntityType.DOMAIN, domain,
            source_name="virustotal",
            source_type=SourceType.API,
            attributes={'vt_data': True}
        )
        result.entities.append(domain_entity)
        
        stats = attrs.get('last_analysis_stats', {})
        if stats.get('malicious', 0) > 0:
            domain_entity.is_malicious = True
            domain_entity.risk_score = min(100, stats['malicious'] * 10)
        
        result.observations.append(self._create_observation(domain_entity.id, {
            'type': 'virustotal_domain',
            'domain': domain,
            'stats': stats,
            'categories': attrs.get('categories', {}),
            'reputation': attrs.get('reputation'),
            'whois': attrs.get('whois'),
            'registrar': attrs.get('registrar'),
            'creation_date': attrs.get('creation_date'),
            'last_dns_records': attrs.get('last_dns_records', []),
            'subdomains': attrs.get('subdomains', [])[:100]
        }))
    
    async def _collect_ip(self, ip: str, result: CollectorResult) -> None:
        session = await self._get_session()
        url = f"{self.BASE_URL}/ip_addresses/{ip}"
        
        async with session.get(url) as resp:
            if resp.status == 404:
                return
            data = await resp.json()
        
        attrs = data.get('data', {}).get('attributes', {})
        
        ip_entity = self._create_entity(
            EntityType.IP, ip,
            source_name="virustotal",
            source_type=SourceType.API,
            attributes={'vt_data': True}
        )
        result.entities.append(ip_entity)
        
        stats = attrs.get('last_analysis_stats', {})
        if stats.get('malicious', 0) > 0:
            ip_entity.is_malicious = True
            ip_entity.risk_score = min(100, stats['malicious'] * 10)
        
        result.observations.append(self._create_observation(ip_entity.id, {
            'type': 'virustotal_ip',
            'ip': ip,
            'stats': stats,
            'asn': attrs.get('asn'),
            'as_owner': attrs.get('as_owner'),
            'country': attrs.get('country'),
            'network': attrs.get('network'),
            'last_https_certificate': attrs.get('last_https_certificate'),
            'communications': attrs.get('last_communicating_files', [])[:50]
        }))
    
    async def _collect_url(self, url: str, result: CollectorResult) -> None:
        session = await self._get_session()
        # URL needs to be base64 encoded without padding
        import base64
        url_id = base64.urlsafe_b64encode(url.encode()).decode().rstrip('=')
        api_url = f"{self.BASE_URL}/urls/{url_id}"
        
        async with session.get(api_url) as resp:
            if resp.status == 404:
                # Submit for analysis
                submit_url = f"{self.BASE_URL}/urls"
                async with session.post(submit_url, data={'url': url}) as submit_resp:
                    if submit_resp.status == 200:
                        submit_data = await submit_resp.json()
                        url_id = submit_data.get('data', {}).get('id')
                        if url_id:
                            # Wait a bit and retry
                            await asyncio.sleep(5)
                            async with session.get(f"{self.BASE_URL}/urls/{url_id}") as retry_resp:
                                if retry_resp.status == 200:
                                    data = await retry_resp.json()
                                else:
                                    return
                    else:
                        return
            else:
                data = await resp.json()
        
        attrs = data.get('data', {}).get('attributes', {})
        
        url_entity = self._create_entity(
            EntityType.URL, url,
            source_name="virustotal",
            source_type=SourceType.API,
            attributes={'vt_data': True}
        )
        result.entities.append(url_entity)
        
        stats = attrs.get('last_analysis_stats', {})
        if stats.get('malicious', 0) > 0:
            url_entity.is_malicious = True
            url_entity.risk_score = min(100, stats['malicious'] * 10)
        
        result.observations.append(self._create_observation(url_entity.id, {
            'type': 'virustotal_url',
            'url': url,
            'stats': stats,
            'final_url': attrs.get('url'),
            'title': attrs.get('title'),
            'last_analysis_date': attrs.get('last_analysis_date')
        }))
    
    def _is_hash(self, target: str) -> bool:
        import re
        return re.match(r'^[a-fA-F0-9]{32,64}$', target) is not None
    
    def _is_domain(self, target: str) -> bool:
        import re
        return re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$', target) is not None
    
    def _is_ip(self, target: str) -> bool:
        import re
        return re.match(r'^(\d{1,3}\.){3}\d{1,3}$', target) is not None
    
    def _is_url(self, target: str) -> bool:
        import re
        return re.match(r'^https?://', target) is not None


@collector(
    name="censys",
    description="Censys internet-wide scan data",
    supported_types=[EntityType.IP, EntityType.DOMAIN, EntityType.CERTIFICATE],
    rate_limit=100,
    timeout=30
)
class CensysCollector(BaseCollector):
    """Censys API integration."""
    
    BASE_URL = "https://search.censys.io/api/v2"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.api_id = self.collectors.api_keys.get('censys_id', '')
        self.api_secret = self.collectors.api_keys.get('censys_secret', '')
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            if self.api_id and self.api_secret:
                auth = aiohttp.BasicAuth(self.api_id, self.api_secret)
            else:
                auth = None
            self.session = aiohttp.ClientSession(
                auth=auth,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        return self.session
    
    async def collect(self, target: str, **kwargs) -> CollectorResult:
        if not self.api_id or not self.api_secret:
            return CollectorResult(errors=["Censys API credentials not configured"])
        
        await self._wait_for_rate_limit()
        job = self._start_job(target, kwargs)
        result = CollectorResult()
        
        try:
            if self._is_ip(target):
                await self._collect_host(target, result)
            elif self._is_domain(target):
                await self._collect_domain(target, result)
        except Exception as e:
            result.errors.append(str(e))
        finally:
            self._complete_job(result)
        
        return result
    
    async def _collect_host(self, ip: str, result: CollectorResult) -> None:
        session = await self._get_session()
        url = f"{self.BASE_URL}/hosts/{ip}"
        
        async with session.get(url) as resp:
            if resp.status == 404:
                return
            data = await resp.json()
        
        host = data.get('result', {})
        
        ip_entity = self._create_entity(
            EntityType.IP, ip,
            source_name="censys",
            source_type=SourceType.API,
            attributes={'censys': True}
        )
        result.entities.append(ip_entity)
        
        # Services
        for service in host.get('services', []):
            port = service.get('port')
            service_name = service.get('service_name', '')
            
            obs = self._create_observation(ip_entity.id, {
                'type': 'censys_service',
                'port': port,
                'service': service_name,
                'banner': service.get('banner', '')[:500],
                'software': service.get('software', []),
                'certificate': service.get('certificate'),
                'jarm': service.get('jarm'),
                'transport': service.get('transport_protocol')
            })
            result.observations.append(obs)
        
        # Location
        if location := host.get('location'):
            obs = self._create_observation(ip_entity.id, {
                'type': 'censys_location',
                'country': location.get('country'),
                'city': location.get('city'),
                'coordinates': location.get('coordinates'),
                'timezone': location.get('timezone')
            })
            result.observations.append(obs)
    
    async def _collect_domain(self, domain: str, result: CollectorResult) -> None:
        session = await self._get_session()
        url = f"{self.BASE_URL}/hosts/search"
        params = {'q': f'parsed.names: {domain}', 'per_page': 100}
        
        async with session.get(url, params=params) as resp:
            data = await resp.json()
        
        for hit in data.get('result', {}).get('hits', []):
            ip = hit.get('ip')
            if ip:
                ip_entity = self._create_entity(EntityType.IP, ip, source_name="censys", source_type=SourceType.API)
                result.entities.append(ip_entity)
                
                dom_entity = self._create_entity(EntityType.DOMAIN, domain, source_name="censys", source_type=SourceType.API)
                result.entities.append(dom_entity)
                result.relationships.append({
                    'source_id': dom_entity.id,
                    'target_id': ip_entity.id,
                    'relationship_type': 'resolves_to',
                    'description': f'{domain} resolves to {ip} (Censys)'
                })
    
    def _is_ip(self, target: str) -> bool:
        import re
        return re.match(r'^(\d{1,3}\.){3}\d{1,3}$', target) is not None
    
    def _is_domain(self, target: str) -> bool:
        import re
        return re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$', target) is not None


@collector(
    name="github",
    description="GitHub code search and reconnaissance",
    supported_types=[EntityType.DOMAIN, EntityType.EMAIL, EntityType.PERSON],
    rate_limit=10,
    timeout=30
)
class GitHubCollector(BaseCollector):
    """GitHub API integration."""
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.token = self.collectors.api_keys.get('github', '')
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            headers = {'Authorization': f'token {self.token}'} if self.token else {}
            headers['Accept'] = 'application/vnd.github.v3+json'
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        return self.session
    
    async def collect(self, target: str, **kwargs) -> CollectorResult:
        if not self.token:
            return CollectorResult(errors=["GitHub token not configured"])
        
        await self._wait_for_rate_limit()
        job = self._start_job(target, kwargs)
        result = CollectorResult()
        
        try:
            if self._is_domain(target):
                await self._search_domain(target, result)
            elif self._is_email(target):
                await self._search_email(target, result)
        except Exception as e:
            result.errors.append(str(e))
        finally:
            self._complete_job(result)
        
        return result
    
    async def _search_domain(self, domain: str, result: CollectorResult) -> None:
        session = await self._get_session()
        
        # Search code for domain references
        url = f"{self.BASE_URL}/search/code"
        params = {'q': f'"{domain}"', 'per_page': 100}
        
        async with session.get(url, params=params) as resp:
            if resp.status == 200:
                data = await resp.json()
                for item in data.get('items', []):
                    repo = item.get('repository', {}).get('full_name')
                    path = item.get('path')
                    html_url = item.get('html_url')
                    
                    obs = self._create_observation(f"domain:{domain}", {
                        'type': 'github_code',
                        'domain': domain,
                        'repository': repo,
                        'file': path,
                        'url': html_url
                    })
                    result.observations.append(obs)
        
        # Search repos with domain in description
        params = {'q': f'{domain} in:description', 'per_page': 50}
        async with session.get(f"{self.BASE_URL}/search/repositories", params=params) as resp:
            if resp.status == 200:
                data = await resp.json()
                for repo in data.get('items', []):
                    obs = self._create_observation(f"domain:{domain}", {
                        'type': 'github_repo',
                        'domain': domain,
                        'repository': repo.get('full_name'),
                        'description': repo.get('description'),
                        'stars': repo.get('stargazers_count'),
                        'url': repo.get('html_url')
                    })
                    result.observations.append(obs)
    
    async def _search_email(self, email: str, result: CollectorResult) -> None:
        session = await self._get_session()
        
        # Search commits by email
        url = f"{self.BASE_URL}/search/commits"
        params = {'q': f'author-email:{email}', 'per_page': 100}
        
        async with session.get(url, params=params) as resp:
            if resp.status == 200:
                data = await resp.json()
                for commit in data.get('items', []):
                    repo = commit.get('repository', {}).get('full_name')
                    message = commit.get('commit', {}).get('message', '')[:200]
                    html_url = commit.get('html_url')
                    
                    obs = self._create_observation(f"email:{email}", {
                        'type': 'github_commit',
                        'email': email,
                        'repository': repo,
                        'message': message,
                        'url': html_url
                    })
                    result.observations.append(obs)
    
    def _is_domain(self, target: str) -> bool:
        import re
        return re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$', target) is not None
    
    def _is_email(self, target: str) -> bool:
        import re
        return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', target) is not None