"""
Web collector for OSINT Independent Platform.
Handles HTTP requests, HTML parsing, and web scraping.
"""
import asyncio
import re
import ssl
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse, parse_qs
from uuid import uuid4

import aiohttp
from bs4 import BeautifulSoup

from .base import BaseCollector, CollectorResult, collector
from ..core.models import Entity, EntityType, Observation, Source, SourceType, ConfidenceLevel


@collector(
    name="web",
    description="Web scraping and HTTP intelligence collector",
    supported_types=[EntityType.DOMAIN, EntityType.URL, EntityType.IP, EntityType.EMAIL],
    rate_limit=30,
    timeout=30
)
class WebCollector(BaseCollector):
    """Web intelligence collector."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.session: Optional[aiohttp.ClientSession] = None
        self._ssl_context = ssl.create_default_context()
        self._ssl_context.check_hostname = False
        self._ssl_context.verify_mode = ssl.CERT_NONE
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            connector = aiohttp.TCPConnector(
                ssl=self._ssl_context,
                limit=10,
                limit_per_host=5
            )
            headers = {
                'User-Agent': self.collector_config.user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers=headers
            )
        return self.session
    
    async def close(self) -> None:
        """Close the session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def collect(self, target: str, **kwargs) -> CollectorResult:
        """Collect web intelligence on a target."""
        await self._wait_for_rate_limit()
        
        job = self._start_job(target, kwargs)
        result = CollectorResult()
        
        try:
            session = await self._get_session()
            
            # Determine target type and collect accordingly
            if self._is_url(target):
                await self._collect_url(session, target, result)
            elif self._is_domain(target):
                await self._collect_domain(session, target, result)
            elif self._is_ip(target):
                await self._collect_ip(session, target, result)
            else:
                result.errors.append(f"Unsupported target type: {target}")
            
        except Exception as e:
            self.logger.error(f"Collection failed for {target}: {e}")
            result.errors.append(str(e))
        finally:
            self._complete_job(result)
        
        return result
    
    def _is_url(self, target: str) -> bool:
        return target.startswith(('http://', 'https://'))
    
    def _is_domain(self, target: str) -> bool:
        return re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$', target) is not None
    
    def _is_ip(self, target: str) -> bool:
        return re.match(r'^(\d{1,3}\.){3}\d{1,3}$', target) is not None
    
    async def _collect_url(self, session: aiohttp.ClientSession, url: str, result: CollectorResult) -> None:
        """Collect from a specific URL."""
        try:
            async with session.get(url, allow_redirects=True) as response:
                content_type = response.headers.get('Content-Type', '')
                text = await response.text()
                
                # Create URL entity
                url_entity = self._create_entity(
                    EntityType.URL, url,
                    name=url,
                    source_name="web",
                    source_type=SourceType.WEB,
                    attributes={'status_code': response.status, 'content_type': content_type}
                )
                result.entities.append(url_entity)
                
                # Create observation
                obs = self._create_observation(url_entity.id, {
                    'url': url,
                    'status_code': response.status,
                    'content_type': content_type,
                    'content_length': len(text),
                    'headers': dict(response.headers)
                }, raw_data=text[:5000])
                result.observations.append(obs)
                
                # Parse HTML
                if 'text/html' in content_type:
                    await self._parse_html(text, url, url_entity.id, result)
                
        except Exception as e:
            self.logger.warning(f"Failed to collect URL {url}: {e}")
            result.errors.append(f"URL {url}: {e}")
    
    async def _collect_domain(self, session: aiohttp.ClientSession, domain: str, result: CollectorResult) -> None:
        """Collect from a domain (both HTTP and HTTPS)."""
        for scheme in ['https', 'http']:
            url = f"{scheme}://{domain}"
            await self._collect_url(session, url, result)
    
    async def _collect_ip(self, session: aiohttp.ClientSession, ip: str, result: CollectorResult) -> None:
        """Collect from an IP address."""
        for scheme in ['https', 'http']:
            url = f"{scheme}://{ip}"
            try:
                await self._collect_url(session, url, result)
            except Exception:
                pass  # Try next scheme
    
    async def _parse_html(self, html: str, base_url: str, source_entity_id: str, result: CollectorResult) -> None:
        """Parse HTML for intelligence."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract emails
        emails = self._extract_emails(html)
        for email in emails:
            entity = self._create_entity(
                EntityType.EMAIL, email,
                source_name="web",
                source_type=SourceType.WEB,
                attributes={'source_url': base_url}
            )
            result.entities.append(entity)
            result.observations.append(self._create_observation(entity.id, {
                'email': email,
                'source_url': base_url,
                'context': 'html_content'
            }))
        
        # Extract links
        links = self._extract_links(soup, base_url)
        for link in links:
            if link != base_url:
                entity = self._create_entity(
                    EntityType.URL, link,
                    source_name="web",
                    source_type=SourceType.WEB,
                    attributes={'source_url': base_url, 'link_type': 'href'}
                )
                result.entities.append(entity)
                result.relationships.append({
                    'source_id': source_entity_id,
                    'target_id': entity.id,
                    'relationship_type': 'links_to',
                    'description': f'Link from {base_url} to {link}'
                })
        
        # Extract metadata
        meta = self._extract_metadata(soup)
        if meta:
            result.observations.append(self._create_observation(source_entity_id, {
                'type': 'metadata',
                'data': meta,
                'source_url': base_url
            }))
        
        # Extract scripts and endpoints
        scripts = self._extract_scripts(soup, base_url)
        for script in scripts:
            entity = self._create_entity(
                EntityType.URL, script,
                source_name="web",
                source_type=SourceType.WEB,
                attributes={'type': 'script', 'source_url': base_url}
            )
            result.entities.append(entity)
        
        # Extract forms
        forms = self._extract_forms(soup, base_url)
        for form in forms:
            result.observations.append(self._create_observation(source_entity_id, {
                'type': 'form',
                'action': form.get('action'),
                'method': form.get('method'),
                'inputs': form.get('inputs', []),
                'source_url': base_url
            }))
    
    def _extract_emails(self, text: str) -> Set[str]:
        """Extract email addresses from text."""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = set(re.findall(pattern, text))
        # Filter out common false positives
        filtered = set()
        for email in emails:
            if not any(fp in email.lower() for fp in ['example.com', 'test.com', 'localhost', 'yourdomain', 'mydomain']):
                filtered.add(email.lower())
        return filtered
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> Set[str]:
        """Extract all links from HTML."""
        links = set()
        for a in soup.find_all('a', href=True):
            href = a['href']
            absolute = urljoin(base_url, href)
            parsed = urlparse(absolute)
            if parsed.scheme in ('http', 'https'):
                links.add(absolute)
        return links
    
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract metadata from HTML head."""
        meta = {}
        for tag in soup.find_all('meta'):
            name = tag.get('name') or tag.get('property') or tag.get('http-equiv')
            content = tag.get('content')
            if name and content:
                meta[name] = content
        return meta
    
    def _extract_scripts(self, soup: BeautifulSoup, base_url: str) -> Set[str]:
        """Extract script sources."""
        scripts = set()
        for script in soup.find_all('script', src=True):
            src = script['src']
            absolute = urljoin(base_url, src)
            parsed = urlparse(absolute)
            if parsed.scheme in ('http', 'https'):
                scripts.add(absolute)
        return scripts
    
    def _extract_forms(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Extract form information."""
        forms = []
        for form in soup.find_all('form'):
            action = form.get('action', '')
            if action:
                action = urljoin(base_url, action)
            inputs = []
            for inp in form.find_all('input'):
                inputs.append({
                    'name': inp.get('name'),
                    'type': inp.get('type', 'text'),
                    'value': inp.get('value', '')
                })
            forms.append({
                'action': action,
                'method': form.get('method', 'GET').upper(),
                'inputs': inputs
            })
        return forms


@collector(
    name="cert",
    description="Certificate Transparency log collector",
    supported_types=[EntityType.DOMAIN],
    rate_limit=10,
    timeout=30
)
class CertificateCollector(BaseCollector):
    """Collect subdomains from Certificate Transparency logs."""
    
    CT_LOGS = [
        "https://crt.sh/?q=%25.{domain}&output=json",
        "https://api.certspotter.com/v1/issuances?domain={domain}&include_subdomains=true&expand=dnames",
    ]
    
    async def collect(self, target: str, **kwargs) -> CollectorResult:
        if not self._is_domain(target):
            return CollectorResult(errors=[f"Invalid domain: {target}"])
        
        await self._wait_for_rate_limit()
        job = self._start_job(target, kwargs)
        result = CollectorResult()
        
        try:
            session = await self._get_session()
            
            for log_url in self.CT_LOGS:
                url = log_url.format(domain=target)
                try:
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            self._process_ct_data(data, target, result)
                except Exception as e:
                    self.logger.warning(f"CT log query failed: {e}")
                    
        except Exception as e:
            result.errors.append(str(e))
        finally:
            self._complete_job(result)
        
        return result
    
    def _process_ct_data(self, data: List[Dict], domain: str, result: CollectorResult) -> None:
        """Process CT log data."""
        seen = set()
        for entry in data:
            names = set()
            if 'name_value' in entry:
                names.update(entry['name_value'].split('\n'))
            elif 'dns_names' in entry:
                names.update(entry['dns_names'])
            elif 'common_name' in entry:
                names.add(entry['common_name'])
            
            for name in names:
                name = name.strip().lower()
                if name.endswith(f'.{domain}') or name == domain:
                    if name not in seen:
                        seen.add(name)
                        entity = self._create_entity(
                            EntityType.DOMAIN, name,
                            source_name="certificate_transparency",
                            source_type=SourceType.CERTIFICATE,
                            attributes={'issuer': entry.get('issuer_name', ''), 
                                      'not_before': entry.get('not_before', ''),
                                      'not_after': entry.get('not_after', '')}
                        )
                        result.entities.append(entity)
                        result.observations.append(self._create_observation(entity.id, {
                            'domain': name,
                            'source': 'certificate_transparency',
                            'raw_entry': entry
                        }))
    
    def _is_domain(self, target: str) -> bool:
        import re
        return re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$', target) is not None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def close(self) -> None:
        if self.session and not self.session.closed:
            await self.session.close()